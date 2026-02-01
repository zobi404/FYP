from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .serializers import ComplianceAuditRequestSerializer, ComplianceAuditResponseSerializer
from .services import ComplianceAuditService
from .models import ComplianceAudit

class ComplianceAuditView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Compliance'],
        request=ComplianceAuditRequestSerializer,
        responses={201: ComplianceAuditResponseSerializer}
    )
    def post(self, request):
        serializer = ComplianceAuditRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        url = serializer.validated_data['url']
        
        # 1. Fetch website data
        website_data = ComplianceAuditService.fetch_website_data(url)
        if "error" in website_data:
            return Response({"error": "Failed to fetch website data", "details": website_data["error"]}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Identify tech stack
        tech_stack = ComplianceAuditService.identify_tech_stack(website_data)
        
        # 3. Generate report via Gemini
        report_markdown, score = ComplianceAuditService.generate_report(url, website_data, tech_stack)
        
        if report_markdown.startswith("Error"):
             return Response({"error": "Failed to generate report", "details": report_markdown}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 4. Generate PDF Report
        import os
        import uuid
        from django.core.files.base import ContentFile
        from django.conf import settings

        # Create a temporary file path
        pdf_filename = f"report_{uuid.uuid4().hex}.pdf"
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp', pdf_filename)
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
        
        ComplianceAuditService.generate_pdf(report_markdown, temp_pdf_path)

        # 5. Save to database
        audit = ComplianceAudit.objects.create(
            maintainer=request.user,
            url=url,
            readiness_score=score,
            report_markdown=report_markdown,
            tech_stack_raw=tech_stack,
            headers_raw=website_data.get('headers', {})
        )
        
        # Open and save the PDF to the model
        with open(temp_pdf_path, 'rb') as f:
            audit.report_pdf.save(pdf_filename, ContentFile(f.read()), save=True)

        # Clean up temp file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        
        response_serializer = ComplianceAuditResponseSerializer(audit)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
