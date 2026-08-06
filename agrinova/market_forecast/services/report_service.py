import io
import datetime
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.units import inch

class ReportService:
    @staticmethod
    def _create_chart(weekly_history, monthly_history):
        """Generate a compact historical price chart."""
        plt.figure(figsize=(7, 2.5)) # Compact size
        
        # Use last 15 days max
        data = weekly_history if weekly_history else (monthly_history[-15:] if monthly_history else [])
        
        if not data:
            plt.text(0.5, 0.5, 'No Recent Data', horizontalalignment='center', verticalalignment='center')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            return buf

        dates = []
        modal_prices = []

        try:
            for item in data:
                dates.append(datetime.datetime.strptime(item['date'], '%Y-%m-%d'))
                modal_prices.append(item.get('modal_price', 0))

            plt.plot(dates, modal_prices, marker='o', color='#10b981', linewidth=2, markersize=4)
            plt.fill_between(dates, modal_prices, 0, color='#10b981', alpha=0.1)

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            plt.gcf().autofmt_xdate()
            
            # Add some padding to y-axis limits to prevent lines touching borders
            y_min = min(modal_prices)
            y_max = max(modal_prices)
            if y_min == y_max:
                y_min -= 100
                y_max += 100
            plt.ylim(bottom=y_min * 0.95, top=y_max * 1.05)

            plt.ylabel('Price (Rs.)', fontsize=9, color='#475569')
            plt.grid(True, axis='y', linestyle='--', alpha=0.5)
            
            # Minimalist styling
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_color('#cbd5e1')
            plt.gca().spines['bottom'].set_color('#cbd5e1')
            plt.tick_params(colors='#475569', labelsize=8)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            return buf
        except Exception:
            plt.close()
            return None

    @staticmethod
    def generate_market_report(data, farm_details, user_details):
        buffer = io.BytesIO()
        # Reduce margins for a more compact single-page layout
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            title=f"Market Advisory Report - {data.get('crop')}"
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#064e3b'), spaceAfter=2, alignment=1, fontName='Helvetica-Bold')
        subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=15, alignment=1)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#16a34a'), spaceBefore=10, spaceAfter=6, fontName='Helvetica-Bold')
        normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#1e293b'), spaceAfter=4)
        bullet_style = ParagraphStyle('Bullet', parent=normal_style, bulletIndent=10, leftIndent=20, spaceAfter=4)
        
        # HEADER
        elements.append(Paragraph("AgriNova", title_style))
        elements.append(Paragraph("AI-Powered Smart Agriculture Platform", subtitle_style))
        elements.append(Paragraph("MARKET ADVISORY REPORT", ParagraphStyle('ReportTitle', parent=title_style, fontSize=14, textColor=colors.HexColor('#0f172a'), spaceAfter=10)))

        # SECTION 1: Farmer Information
        report_id = str(uuid.uuid4())[:8].upper()
        gen_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        info_data = [
            ["Farmer Name:", user_details.get('name', 'N/A'), "Crop:", data.get('crop', 'N/A')],
            ["Farm Name:", farm_details.get('farm_name', 'N/A'), "Selected Market:", data.get('market', 'N/A')],
            ["Location:", f"{data.get('district', 'N/A')}, {data.get('state', 'N/A')}", "Report Date:", gen_time],
            ["Data Source:", "AGMARKNET (data.gov.in)", "Report ID:", report_id],
        ]
        
        info_table = Table(info_data, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 5))

        # SECTION 2: Current Market Snapshot
        elements.append(Paragraph("Current Market Snapshot", section_style))
        current_price = data.get('current_price', {})
        trend = data.get('trend', 'Stable')
        
        snap_data = [
            ["Current Modal Price", "Minimum Price", "Maximum Price", "Arrival Quantity", "Market Trend"],
            [f"Rs. {current_price.get('modal_price', 0)}", f"Rs. {current_price.get('minimum_price', 0)}", f"Rs. {current_price.get('maximum_price', 0)}", f"{current_price.get('arrival_quantity', 'N/A')} T", trend.upper()]
        ]
        snap_table = Table(snap_data, colWidths=[1.44*inch]*5)
        snap_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#475569')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,1), (0,1), colors.HexColor('#15803d')), # Modal price green
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(snap_table)

        # SECTION 7: Decision Box
        # We put it high up so it's immediately visible
        elements.append(Spacer(1, 10))
        recommendation_text = data.get('predictions', {}).get('recommendation', 'Hold and monitor market closely.')
        
        # Determine primary action
        rec_lower = recommendation_text.lower()
        if 'sell' in rec_lower and 'immediate' in rec_lower:
            action, bg_color, text_color = "✔ SELL IMMEDIATELY", '#dcfce7', '#166534'
        elif 'sell' in rec_lower:
            action, bg_color, text_color = "✔ FAVORABLE TO SELL", '#dcfce7', '#166534'
        elif 'wait' in rec_lower or 'hold' in rec_lower:
            action, bg_color, text_color = "WAIT FOR BETTER PRICE", '#fef3c7', '#92400e'
        elif 'store' in rec_lower:
            action, bg_color, text_color = "STORE CROP", '#e0e7ff', '#3730a3'
        else:
            action, bg_color, text_color = "MONITOR MARKET", '#f1f5f9', '#334155'
            
        decision_data = [[Paragraph(f"<font color='{text_color}'><b>{action}</b></font><br/><font size=9>{recommendation_text}</font>", ParagraphStyle('Decision', alignment=1, leading=14))]]
        decision_table = Table(decision_data, colWidths=[7.2*inch])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(text_color)),
            ('PADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(KeepTogether([decision_table]))
        
        # SECTION 3: Best Market Recommendation
        elements.append(Paragraph("Best Market Recommendation", section_style))
        markets_data = data.get('markets_data', [])
        markets_data.sort(key=lambda x: x.get('modal_price', 0), reverse=True)
        
        comp_data = [["Rank", "Market", "Modal Price", "Min Price", "Max Price", "Arrivals"]]
        for idx, m in enumerate(markets_data[:3]): # Top 3 only
            market_name = m.get('market', 'Unknown')
            if idx == 0:
                market_name = f"{market_name} (Best Option)"
            comp_data.append([
                str(idx + 1),
                market_name,
                f"Rs. {m.get('modal_price', 0)}",
                f"Rs. {m.get('minimum_price', 0)}",
                f"Rs. {m.get('maximum_price', 0)}",
                f"{m.get('arrival_quantity', 'N/A')} T"
            ])
            
        comp_table = Table(comp_data, colWidths=[0.5*inch, 2.5*inch, 1.1*inch, 1.1*inch, 1.1*inch, 0.9*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
            # Highlight best market
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#ecfdf5')),
            ('FONTNAME', (1,1), (1,1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#059669')),
        ]))
        elements.append(comp_table)

        # SECTION 4 & 6: Farmer Advisory & Key Observations
        elements.append(Paragraph("Key Market Observations", section_style))
        
        price_spread = current_price.get('maximum_price', 0) - current_price.get('minimum_price', 0)
        top_market = markets_data[0].get('market') if markets_data else data.get('market')
        
        obs1 = f"Highest modal price observed at {top_market}."
        obs2 = f"Market arrivals currently stand at {current_price.get('arrival_quantity', 'N/A')} Tons."
        obs3 = f"Price spread (Max - Min) is Rs. {price_spread:,.2f}."
        obs4 = f"Market trend is currently {trend.lower()}."
        
        elements.append(Paragraph(f"• {obs1}", bullet_style))
        elements.append(Paragraph(f"• {obs2}", bullet_style))
        elements.append(Paragraph(f"• {obs3}", bullet_style))
        elements.append(Paragraph(f"• {obs4}", bullet_style))

        # SECTION 5: Price Trend (Chart)
        elements.append(Paragraph("Price Trend (Recent)", section_style))
        chart_buffer = ReportService._create_chart(data.get('weekly_price_history', []), data.get('monthly_price_history', []))
        if chart_buffer:
            elements.append(RLImage(chart_buffer, width=6*inch, height=2.14*inch))

        # SECTION 8: Important Notes
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Important Notes:", ParagraphStyle('NotesHeading', parent=normal_style, fontName='Helvetica-Bold')))
        elements.append(Paragraph("• Prices may vary throughout the day. Verify current rates before transporting produce.", bullet_style))
        elements.append(Paragraph("• Recommendations are based on official AGMARKNET data and AI analysis.", bullet_style))
        
        # Build PDF
        doc.build(elements, onFirstPage=ReportService._add_page_number, onLaterPages=ReportService._add_page_number)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        footer_text = "Generated by AgriNova | Official Data Source: AGMARKNET (data.gov.in) | For agricultural decision support only."
        canvas.drawString(0.5*inch, 0.3*inch, footer_text)
        canvas.restoreState()
