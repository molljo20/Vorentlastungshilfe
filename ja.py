import streamlit as st
import re
from typing import Dict, List, Tuple, Optional
import pdfplumber
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from io import BytesIO
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd

# ============================================
# DATENMODELL
# ============================================

@dataclass
class VokabelEintrag:
    """Repräsentiert einen Vokabeleintrag aus der PDF"""
    position: int               # Nummer aus der ersten Spalte
    griechisch: str             # Hauptwort (linke Spalte, fett)
    stammformen: str = ""       # Vollständiger Inhalt der mittleren Spalte
    zusatz: str = ""           # (optional, nicht verwendet)
    bedeutungen: List[str] = field(default_factory=list)
    gefunden: bool = False
    original_zeile: str = ""

# ============================================
# OMEGA-WORTSCHATZ (VOLLSTÄNDIG, UNVERÄNDERT)
# ============================================
# ... [vollständiger Omega-Wortschatz, identisch zum vorherigen Code] ...
# Aus Platzgründen hier nicht wiederholt – bitte den bereits existierenden,
# vollständigen Omega-Wortschatz aus der vorherigen Antwort verwenden.
# (Die 800+ Einträge sind exakt gleich, nur der Parser ändert sich.)
# ============================================

class OmegaWortschatz:
    # ... (vollständig wie gehabt) ...
    pass

# ============================================
# PDF-PARSER – NEU: NUR HAUPTWORT + STAMMFORMEN
# ============================================

class VokabelPDFParser:
    """Extrahiert Vokabeln aus dem spezifischen 3‑Spalten-Format:
       - Linke Spalte: Nummer + fettes Hauptwort
       - Mittlere Spalte: Stammformen / Zusatzangaben
       - Rechte Spalte: leer (wird mit Bedeutung gefüllt)
    """
    
    def __init__(self):
        self.omega = OmegaWortschatz()
        # Griechische Artikel (häufigste Formen) – werden beim Hauptwort übersprungen
        self.artikel = {
            'ὁ', 'ἡ', 'τό', 'τὸ', 'οἱ', 'αἱ', 'τά', 'τὰ',
            'τὸν', 'τὴν', 'τοῦ', 'τῆς', 'τῷ', 'τῇ', 'τούς', 'τάς'
        }
    
    def parse_pdf(self, pdf_file) -> List[VokabelEintrag]:
        """Parst die PDF und extrahiert für jede Zeile: Nummer, Hauptwort, Stammformen"""
        eintraege = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    eintraege.extend(self._parse_text(text))
        # Nach Nummer sortieren (falls PDF-Seiten durcheinander)
        eintraege.sort(key=lambda x: x.position)
        return eintraege
    
    def _parse_text(self, text: str) -> List[VokabelEintrag]:
        """Extrahiert Zeile für Zeile nach dem Muster: NUMMER + HAUPTWORT + REST (Stammformen)"""
        eintraege = []
        lines = text.split('\n')
        
        # Unicode-Bereich für vollständiges Griechisch (mit Akzenten, Spiritus etc.)
        greek_pattern = r'([\u0370-\u03FF\u1F00-\u1FFF]+)'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # ---- 1. Nummer am Zeilenanfang extrahieren ----
            num_match = re.match(r'^(\d+)', line)
            if not num_match:
                continue
            num = int(num_match.group(1))
            rest = line[num_match.end():].strip()
            
            # ---- 2. Alle griechischen Wörter im Rest finden ----
            greek_words = re.findall(greek_pattern, rest)
            if not greek_words:
                continue
            
            # ---- 3. Hauptwort bestimmen (erstes Wort, das KEIN Artikel ist) ----
            hauptwort = None
            for w in greek_words:
                if w not in self.artikel:
                    hauptwort = w
                    break
            if hauptwort is None:
                # Falls alle Wörter Artikel sind (unwahrscheinlich) → erstes nehmen
                hauptwort = greek_words[0]
            
            # ---- 4. Alles nach der Nummer = Stammformenspalte ----
            stammformen = rest   # komplette mittlere Spalte
            
            # ---- 5. Vokabeleintrag anlegen ----
            eintrag = VokabelEintrag(
                position=num,
                griechisch=hauptwort,
                stammformen=stammformen,
                original_zeile=line
            )
            
            # ---- 6. Bedeutung aus Omega-Wortschatz holen ----
            bedeutungen, gefunden, _ = self.omega.finde_bedeutung(hauptwort)
            eintrag.bedeutungen = bedeutungen if bedeutungen else []
            eintrag.gefunden = gefunden
            
            eintraege.append(eintrag)
        
        return eintraege


# ============================================
# PDF-GENERATOR (UNVERÄNDERT)
# ============================================

class PDFGenerator:
    @staticmethod
    def erstelle_pdf(eintraege: List[VokabelEintrag]) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        titel = Paragraph("Vokabelliste mit Bedeutungen", styles['Heading1'])
        story.append(titel)
        story.append(Spacer(1, 0.5*cm))
        
        data = [['Nr.', 'Griechisch', 'Stammformen (PDF)', 'Bedeutungen']]
        for e in eintraege:
            data.append([
                str(e.position),
                e.griechisch,
                e.stammformen,
                '; '.join(e.bedeutungen) if e.bedeutungen else '⚠️ nicht gefunden'
            ])
        
        table = Table(data, colWidths=[1.5*cm, 4*cm, 5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(table)
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            "Vokabeldaten basierend auf dem Omega-Wortschatz von Ulrich Gebhardt, Freiburg - CC BY-NC-SA 4.0",
            styles['Italic']
        ))
        doc.build(story)
        buffer.seek(0)
        return buffer


# ============================================
# STREAMLIT UI (UNVERÄNDERT, bis auf Anzeige der Stammformen)
# ============================================

def main():
    st.set_page_config(page_title="Altgriechisch Vokabeltrainer", page_icon="📚", layout="wide")
    st.title("📚 Altgriechisch Vokabeltrainer")
    st.markdown("---")
    
    with st.sidebar:
        st.header("ℹ️ Info")
        st.markdown("""
        **Erwartetes PDF-Format:**  
        • Linke Spalte: Nummer + **fettes Hauptwort**  
        • Mittlere Spalte: Stammformen / Zusatzangaben  
        • Rechte Spalte: leer (wird von der App gefüllt)
        
        **Omega-Wortschatz:**  
        Über 800 Wörter, CC BY-NC-SA 4.0, Ulrich Gebhardt
        """)
        st.markdown("---")
        st.caption("Erstellt für Altgriechisch-Unterricht")
    
    uploaded_file = st.file_uploader("📤 Vokabellisten-PDF auswählen", type=['pdf'])
    
    if uploaded_file:
        with st.spinner("📖 Analysiere PDF und suche Bedeutungen..."):
            parser = VokabelPDFParser()
            eintraege = parser.parse_pdf(uploaded_file)
        
        if eintraege:
            st.success(f"✅ {len(eintraege)} Vokabeln gefunden!")
            
            gefunden = sum(1 for e in eintraege if e.gefunden)
            col1, col2, col3 = st.columns(3)
            col1.metric("Gesamt", len(eintraege))
            col2.metric("Gefunden", gefunden, f"{gefunden/len(eintraege)*100:.0f}%")
            col3.metric("Nicht gefunden", len(eintraege)-gefunden)
            
            st.markdown("---")
            st.subheader("✏️ Manuelle Korrektur")
            st.caption("Bei Bedarf können Sie die Bedeutungen hier anpassen.")
            
            korrigierte = []
            for i, e in enumerate(eintraege):
                with st.expander(f"{e.position}. {e.griechisch}", expanded=False):
                    col_a, col_b = st.columns([1,3])
                    with col_a:
                        st.markdown(f"**Gefunden:** {'✅' if e.gefunden else '❌'}")
                        st.markdown(f"**Stammformen:** {e.stammformen}")
                    with col_b:
                        aktuell = '; '.join(e.bedeutungen) if e.bedeutungen else ''
                        neu = st.text_area("Bedeutung(en)", value=aktuell, key=f"korr_{i}", height=80)
                        if neu and neu != aktuell:
                            e.bedeutungen = [b.strip() for b in neu.split(';')]
                            e.gefunden = True
                            st.success("✓ korrigiert")
                    korrigierte.append(e)
            
            st.markdown("---")
            st.subheader("📥 Export")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 PDF erstellen", type="primary"):
                    pdf_data = PDFGenerator.erstelle_pdf(korrigierte)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button("⬇️ PDF herunterladen", pdf_data, f"vokabeln_{ts}.pdf", "application/pdf")
            with col2:
                if st.button("📊 CSV exportieren"):
                    df = pd.DataFrame([{
                        'Nr.': e.position,
                        'Griechisch': e.griechisch,
                        'Stammformen': e.stammformen,
                        'Bedeutungen': '; '.join(e.bedeutungen) if e.bedeutungen else '',
                        'Gefunden': e.gefunden
                    } for e in korrigierte])
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button("⬇️ CSV herunterladen", csv, f"vokabeln_{ts}.csv", "text/csv")
            
            st.markdown("---")
            st.subheader("👁️ Vorschau (erste 10)")
            preview_df = pd.DataFrame([{
                'Nr.': e.position, 'Griechisch': e.griechisch,
                'Bedeutung': '; '.join(e.bedeutungen)[:50] + ('…' if len('; '.join(e.bedeutungen))>50 else ''),
                'Status': '✅' if e.gefunden else '❌'
            } for e in korrigierte[:10]])
            st.dataframe(preview_df, use_container_width=True)
            if len(korrigierte) > 10:
                st.caption(f"*… und {len(korrigierte)-10} weitere*")
        else:
            st.warning("⚠️ Keine Zeilen mit Nummer + griechischem Wort gefunden.")
    else:
        st.info("👈 Bitte laden Sie eine PDF im beschriebenen 3‑Spalten-Format hoch.")
        st.markdown("""
        **Beispiel einer gültigen Zeile:**  
        `1ὁ ἀνήρ (1)τοῦ ἀνδρός`  
        → Hauptwort: `ἀνήρ`  
        → Stammformen: `ὁ ἀνήρ (1)τοῦ ἀνδρός`  
        → Bedeutung wird automatisch ergänzt.
        """)

if __name__ == "__main__":
    main()
