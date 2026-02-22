"""
PDF Report Generator for AthSys
Generates professional PDF reports for races, results, and statistics
"""

from datetime import datetime
from io import BytesIO
import json
from typing import List, Dict, Any

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.colors import HexColor, black, white, grey
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self, title: str = "AthSys Report", author: str = "AthSys"):
        self.title = title
        self.author = author
        self.page_size = letter
        self.margins = 0.75 * inch
        
    def generate_race_report(self, race_data: Dict, events: List, results: List) -> BytesIO:
        """Generate PDF report for a race"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_json_fallback("race_report", {
                "race": race_data,
                "events": events,
                "results": results
            })
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margins,
            leftMargin=self.margins,
            topMargin=self.margins,
            bottomMargin=self.margins,
            title=self.title,
            author=self.author
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"<b>{race_data.get('name', 'Race Report')}</b>",
            styles['Title']
        )
        story.append(title)
        
        # Race Details
        race_info = [
            ['Race Information', ''],
            ['Date', race_data.get('date', 'N/A')],
            ['Location', race_data.get('location', 'N/A')],
            ['Status', race_data.get('status', 'N/A')],
            ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        race_table = Table(race_info, colWidths=[2*inch, 4*inch])
        race_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0F0F0')),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(race_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Events
        if events:
            story.append(Paragraph("<b>Events</b>", styles['Heading2']))
            
            event_data = [['Event Name', 'Category', 'Distance', 'Participants']]
            for event in events:
                event_data.append([
                    event.get('name', ''),
                    event.get('category', ''),
                    event.get('distance', ''),
                    str(len([r for r in results if r.get('event_id') == event.get('id')]))
                ])
            
            event_table = Table(event_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F5F5F5')])
            ]))
            
            story.append(event_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Results
        if results:
            story.append(PageBreak())
            story.append(Paragraph("<b>Results</b>", styles['Heading2']))
            
            result_data = [['Position', 'Athlete', 'Time', 'Status', 'Record']]
            for result in results[:50]:  # Limit to first 50
                result_data.append([
                    str(result.get('position', '')),
                    result.get('athlete_name', 'Unknown'),
                    result.get('time', ''),
                    result.get('status', ''),
                    '★' if result.get('is_record') else ''
                ])
            
            result_table = Table(result_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F5F5F5')])
            ]))
            
            story.append(result_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            f"<b>AthSys</b> - Elite Athletics Management System | Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle(
                'footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=grey,
                alignment=1  # Center
            )
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_results_report(self, results: List[Dict], event_info: Dict = None) -> BytesIO:
        """Generate PDF report for competition results"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_json_fallback("results_report", {
                "event": event_info,
                "results": results
            })
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margins,
            leftMargin=self.margins,
            topMargin=self.margins,
            bottomMargin=self.margins
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        event_name = event_info.get('name', 'Results Report') if event_info else 'Results Report'
        title = Paragraph(f"<b>{event_name}</b>", styles['Title'])
        story.append(title)
        
        if event_info:
            story.append(Paragraph(
                f"<b>Date:</b> {event_info.get('date', 'N/A')} | "
                f"<b>Location:</b> {event_info.get('location', 'N/A')}",
                styles['Normal']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Results Table
        data = [['Pos', 'Athlete', 'Country', 'Time/Score', 'Status', 'Record']]
        
        for result in results:
            data.append([
                str(result.get('position', '')),
                result.get('athlete_name', 'Unknown'),
                result.get('country', ''),
                result.get('time', result.get('score', '')),
                result.get('status', 'Finished'),
                '★ WR' if result.get('world_record') else ('★ CR' if result.get('championship_record') else '')
            ])
        
        table = Table(data, colWidths=[0.6*inch, 2*inch, 1.2*inch, 1.5*inch, 1*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F9F9F9')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*inch))
        
        # Summary
        story.append(Paragraph(
            f"<b>Total Finishers:</b> {len([r for r in results if r.get('status') == 'Finished'])} | "
            f"<b>DNF:</b> {len([r for r in results if r.get('status') == 'DNF'])}",
            styles['Normal']
        ))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"Generated by AthSys on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=grey)
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_statistics_report(self, stats: Dict[str, Any]) -> BytesIO:
        """Generate PDF statistics report"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_json_fallback("stats_report", stats)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margins,
            leftMargin=self.margins,
            topMargin=self.margins,
            bottomMargin=self.margins
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph("<b>AthSys Statistics Report</b>", styles['Title']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics Table
        stats_data = [['Statistic', 'Value']]
        for key, value in stats.items():
            key_display = key.replace('_', ' ').title()
            stats_data.append([key_display, str(value)])
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F0F0F0')])
        ]))
        
        story.append(stats_table)
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _generate_json_fallback(report_type: str, data: Dict) -> BytesIO:
        """Fallback: return JSON when reportlab is not available"""
        buffer = BytesIO()
        output = {
            "report_type": report_type,
            "generated": datetime.now().isoformat(),
            "note": "ReportLab not installed. Download and install: pip install reportlab",
            "data": data
        }
        buffer.write(json.dumps(output, indent=2, default=str).encode('utf-8'))
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def is_available() -> bool:
        """Check if PDF generation is available"""
        return REPORTLAB_AVAILABLE


# API Integration Functions

def generate_race_pdf(race_id: int, db_session) -> tuple:
    """
    Generate PDF for a specific race
    Returns: (BytesIO buffer, filename)
    """
    from models import Race, Event, Result
    
    try:
        race = db_session.query(Race).filter(Race.id == race_id).first()
        if not race:
            return None, "Race not found"
        
        events = db_session.query(Event).filter(Event.race_id == race_id).all()
        results = db_session.query(Result).join(Event).filter(Event.race_id == race_id).all()
        
        generator = PDFReportGenerator(title=f"{race.name} Report")
        
        race_data = {
            'name': race.name,
            'date': race.date.strftime('%Y-%m-%d'),
            'location': race.location,
            'status': race.status
        }
        
        events_data = [e.to_dict() for e in events]
        results_data = [r.to_dict() for r in results]
        
        pdf_buffer = generator.generate_race_report(race_data, events_data, results_data)
        filename = f"race_{race_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return pdf_buffer, filename
    
    except Exception as e:
        return None, str(e)


def generate_results_pdf(event_id: int, db_session) -> tuple:
    """
    Generate PDF for event results
    Returns: (BytesIO buffer, filename)
    """
    from models import Event, Result
    
    try:
        event = db_session.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None, "Event not found"
        
        results = db_session.query(Result).filter(Result.event_id == event_id).order_by(Result.position).all()
        
        generator = PDFReportGenerator(title=f"{event.name} Results")
        
        event_data = {
            'name': event.name,
            'date': event.date.strftime('%Y-%m-%d') if hasattr(event, 'date') else 'N/A',
            'location': getattr(event, 'location', 'N/A')
        }
        
        results_data = [r.to_dict() for r in results]
        
        pdf_buffer = generator.generate_results_pdf(results_data, event_data)
        filename = f"results_{event_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return pdf_buffer, filename
    
    except Exception as e:
        return None, str(e)
