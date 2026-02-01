import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from django.conf import settings
import os
import json

class ComplianceAuditService:
    @staticmethod
    def fetch_website_data(url):
        try:
            response = requests.get(url, timeout=10)
            headers = dict(response.headers)
            html_content = response.text[:5000] # Limit to 5k chars for prompt
            
            # Basic structural analysis
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tags = {tag.get('name', tag.get('property')): tag.get('content') for tag in soup.find_all('meta')}
            
            return {
                "headers": headers,
                "html_snippet": html_content,
                "meta_tags": meta_tags,
                "status_code": response.status_code
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def identify_tech_stack(data):
        # Basic fingerprinting based on headers and tags
        headers = data.get('headers', {})
        html = data.get('html_snippet', '')
        
        stack = []
        if 'X-Powered-By' in headers:
            stack.append(headers['X-Powered-By'])
        if 'server' in headers:
            stack.append(headers['server'])
        
        # Look for common patterns
        if 'next-head-count' in html: stack.append("Next.js")
        if 'react' in html.lower(): stack.append("React")
        if 'vue' in html.lower(): stack.append("Vue")
        if 'django' in html.lower(): stack.append("Django")
        
        return stack

    @staticmethod
    def generate_report(url, raw_data, tech_stack):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "Error: GEMINI_API_KEY not found in environment.", 0

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        Act as a Lead Cybersecurity Compliance Auditor specializing in Global (SOC2, HIPAA) and Pakistani (PSS Framework, PECA 2016, Personal Data Protection Bill 2025) regulations.

        ### TASK:
        Analyze the provided website technical data and generate a "Compliance Readiness Audit." The goal is to help a Product owner/maintainer understand their security gaps before uploading their project on this platform.

        ### TECHNICAL DATA TO ANALYZE:
        - URL: {url}
        - Headers: {json.dumps(raw_data.get('headers', {}))}
        - Tech Stack: {json.dumps(tech_stack)}
        - HTML Security Snippets: {raw_data.get('html_snippet', '')}

        ### REPORT STRUCTURE:
        1. EXECUTIVE SUMMARY: Provide a "Readiness Score" from 0-100.
        2. GLOBAL COMPLIANCE (SOC2/HIPAA): 
           - Analyze if SSL/TLS, Security Headers (CSP, HSTS), and Data Encryption are sufficient.
3. PAKISTAN REGULATORY ALIGNMENT:
   - PSS (Pakistan Security Standards): Check against mandatory 2026 certification requirements.
   - PECA 2016: Verify if the site has a 'Terms of Service' that authorizes security research.
   - PDPB 2025 (Data Protection): Check for a Privacy Policy regarding local data residency.
4. ACTIONABLE REMEDIATION: List top 3 high-priority fixes to pass an audit.

        ### OUTPUT FORMAT:
        Return the report in clean Markdown. At the end of the report, add a line "SCORE: [number]" where [number] is the Readiness Score you assigned.
        Do not use conversational filler. Use professional, authoritative language.
        """

        try:
            response = model.generate_content(prompt)
            report_text = response.text
            
            # Extract score
            score = 0
            if "SCORE:" in report_text:
                try:
                    score_part = report_text.split("SCORE:")[1].strip().split('\n')[0]
                    score = int(''.join(filter(str.isdigit, score_part)))
                except:
                    score = 50
            
            return report_text, score
        except Exception as e:
            return f"Error generating report: {str(e)}", 0

    @staticmethod
    def generate_pdf(report_markdown, output_path):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom style for the report
        report_style = ParagraphStyle(
            'ReportStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10
        )
        
        elements = []
        
        # Basic parsing of markdown (just headings and paragraphs for now)
        lines = report_markdown.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.1 * inch))
                continue
                
            if line.startswith('###'):
                elements.append(Paragraph(line.replace('###', '').strip(), styles['Heading3']))
            elif line.startswith('##'):
                elements.append(Paragraph(line.replace('##', '').strip(), styles['Heading2']))
            elif line.startswith('#'):
                elements.append(Paragraph(line.replace('#', '').strip(), styles['Heading1']))
            else:
                # Robust bold replacement using regex to ensure balanced <b></b> tags
                import re
                line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Escape & since ReportLab's XML parser will choke on it
                line = line.replace('&', '&amp;')
                elements.append(Paragraph(line, report_style))
                
        doc.build(elements)
        return output_path

