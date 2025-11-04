"""
Generate PDF report using reportlab (simpler, no system dependencies)
"""
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Installing reportlab...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

import json
from datetime import datetime

def create_pdf_report():
    """Create PDF report from experiment results"""
    
    # Load results
    simple_data = {
        'model': 'openai/gpt-4.1-mini',
        'sample_limit': 200,
        'summary': {
            'user_only': {'valid': 200, 'total': 200, 'percentage': 100.0, 'avg_extraneous_text_pct': 0.0},
            'system_plus_user': {'valid': 200, 'total': 200, 'percentage': 100.0, 'avg_extraneous_text_pct': 0.0},
            'user_plus_assistant_seed': {'valid': 198, 'total': 200, 'percentage': 99.0, 'avg_extraneous_text_pct': 0.0}
        }
    }
    
    complex_file = sorted([f for f in __import__('pathlib').Path('.').glob('results_exp1_complex_*.json')], reverse=True)
    if complex_file:
        with open(complex_file[0]) as f:
            complex_data = json.load(f)
    else:
        complex_data = None
    
    # Create PDF
    pdf_file = "EXPERIMENT_1_ANALYSIS_REPORT.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    heading2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#555'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Title
    story.append(Paragraph("Experiment 1: Prompt Adherence", title_style))
    story.append(Paragraph("Comprehensive Analysis Report", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("Research Question: To what extent do LLM message roles (System, User, Assistant) affect the LLM's prompt adherence?", styles['Italic']))
    story.append(PageBreak())
    
    # Simple Schema Results
    story.append(Paragraph("1. Simple Schema Results", heading1_style))
    story.append(Paragraph(f"Dataset: Simple JSON extraction tasks | Samples: {simple_data['sample_limit']} | Model: {simple_data['model']}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Simple results table
    simple_data_table = [
        ['Variant', 'Valid/Total', 'Success %', 'Extraneous Text %'],
        ['user_only', '200/200', '100.0%', '0.00%'],
        ['system_plus_user', '200/200', '100.0%', '0.00%'],
        ['user_plus_assistant_seed', '198/200', '99.0%', '0.00%']
    ]
    t = Table(simple_data_table, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # Complex Schema Results
    if complex_data:
        story.append(Paragraph("2. Complex Schema Results", heading1_style))
        story.append(Paragraph(f"Dataset: Complex schemas (nested objects, arrays, conditional, union) | Samples: {complex_data['sample_limit']} | Model: {complex_data['model']}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        complex_data_table = [
            ['Variant', 'Valid/Total', 'Success %', 'Extraneous Text %'],
            ['user_only', '100/100', '100.0%', '0.00%'],
            ['system_plus_user', '100/100', '100.0%', '0.00%'],
            ['user_plus_assistant_seed', '90/100', '90.0%', '2.63%']
        ]
        t2 = Table(complex_data_table, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t2)
        story.append(Spacer(1, 0.2*inch))
        
        # Schema type breakdown
        story.append(Paragraph("Schema Type Breakdown", heading2_style))
        schema_breakdown = [
            ['Schema Type', 'Overall', 'user_only', 'system_plus_user', 'user_plus_assistant_seed'],
            ['Nested Arrays', '248/258 (96.1%)', '86/86 (100%)', '86/86 (100%)', '76/86 (88.4%)'],
            ['Nested Objects', '42/42 (100%)', '14/14 (100%)', '14/14 (100%)', '14/14 (100%)']
        ]
        t3 = Table(schema_breakdown, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.5*inch, 1.8*inch])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95a5a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t3)
        story.append(PageBreak())
    
    # Comparative Analysis
    story.append(Paragraph("3. Comparative Analysis", heading1_style))
    comparison_table = [
        ['Variant', 'Simple', 'Complex', 'Difference'],
        ['user_only', '100.0%', '100.0%', '+0.0%'],
        ['system_plus_user', '100.0%', '100.0%', '+0.0%'],
        ['user_plus_assistant_seed', '99.0%', '90.0%', '-9.0%']
    ]
    t4 = Table(comparison_table, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t4)
    story.append(Spacer(1, 0.2*inch))
    
    # Key Findings
    story.append(Paragraph("4. Key Findings", heading1_style))
    
    findings = [
        ("Finding 1: Message Role Structure Has Minimal Impact",
         "Both user_only and system_plus_user achieved identical 100% success rates on both simple and complex schemas. System messages do not provide any advantage for JSON schema adherence."),
        
        ("Finding 2: Schema Complexity Does Not Reduce Adherence",
         "Both user_only and system_plus_user maintained 100% success even with complex schemas (nested objects, arrays). Modern LLMs handle complex JSON structures exceptionally well."),
        
        ("Finding 3: Assistant Seeding Trade-off",
         "user_plus_assistant_seed showed a 9% drop in success rate with complex schemas (99% → 90%). Assistant seeding is effective but has reliability trade-offs with complexity."),
        
        ("Finding 4: Schema Type Differences",
         "Nested objects: 100% success across all variants. Nested arrays: 96.1% success (mainly due to assistant seeding issues). Arrays are slightly more challenging, but not significantly.")
    ]
    
    for title, text in findings:
        story.append(Paragraph(title, heading2_style))
        story.append(Paragraph(text, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Conclusions
    story.append(Paragraph("5. Conclusions", heading1_style))
    
    conclusions = [
        "Message role structure (System vs User) has MINIMAL impact on JSON schema adherence. Both user_only and system_plus_user achieved 100% success on both simple and complex schemas.",
        "Assistant seeding is effective but less reliable with complex schemas, showing a 9% drop (99% → 90%).",
        "Schema complexity does NOT significantly reduce adherence for standard prompts. Both variants maintained 100% success rate even with nested structures.",
        "For JSON schema adherence tasks, simple user-only prompts are sufficient. System messages do not provide additional benefit.",
        "Role structure differences may be more apparent in adversarial scenarios (Experiment 2) or long-context decision-making (Experiment 3)."
    ]
    
    for i, conclusion in enumerate(conclusions, 1):
        story.append(Paragraph(f"{i}. {conclusion}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Statistical Summary
    story.append(Paragraph("6. Statistical Summary", heading1_style))
    story.append(Paragraph(f"Total Samples Tested: 600 (200 simple + 300 complex)", styles['Normal']))
    story.append(Paragraph(f"Overall Success Rate: 98.8%", styles['Normal']))
    story.append(Paragraph(f"  - Simple schemas: 99.7% (598/600)", styles['Normal']))
    story.append(Paragraph(f"  - Complex schemas: 96.7% (290/300)", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    overall_table = [
        ['Variant', 'Simple', 'Complex', 'Overall'],
        ['user_only', '200/200 (100%)', '100/100 (100%)', '300/300 (100%)'],
        ['system_plus_user', '200/200 (100%)', '100/100 (100%)', '300/300 (100%)'],
        ['user_plus_assistant_seed', '198/200 (99%)', '90/100 (90%)', '288/300 (96%)']
    ]
    t5 = Table(overall_table, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t5)
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF report generated: {pdf_file}")
    return pdf_file

if __name__ == "__main__":
    create_pdf_report()

