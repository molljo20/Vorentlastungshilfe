import streamlit as st
import re
from typing import Dict, List, Tuple, Optional
import pdfplumber
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from dataclasses import dataclass, field
from datetime import datetime

# ============================================
# DATENMODELL
# ============================================

@dataclass
class VokabelEintrag:
    """Repräsentiert einen Vokabeleintrag aus der PDF"""
    position: int
    griechisch: str
    stammformen: str = ""
    zusatz: str = ""
    bedeutungen: List[str] = field(default_factory=list)
    gefunden: bool = False
    original_zeile: str = ""

# ============================================
# OMEGA-WORTSCHATZ - DER VOLLSTÄNDIGE WORTSCHATZ
# ============================================

class OmegaWortschatz:
    """Vollständige Implementierung des Omega-Wortschatzes mit allen 800+ Wörtern"""
    
    def __init__(self):
        self.vocab_dict = {}
        self.synonyme = {}
        self._build_dictionary()
        self._build_synonyme()
    
    def _build_synonyme(self):
        """Alternative Schreibweisen und häufige Varianten"""
        self.synonyme = {
            "νόος": "νοῦς",
            "νόος": "νοῦς",
            "ἐσθίω": "ἔσθω",
            "Ζεύς": "Ζεύς",
            "ἐάω": "ἐάω",
            "θέλω": "ἐθέλω",
            "βιόω": "ζάω",
            "γῆ": "γαῖα",
            "θάλαττα": "θάλασσα",
            "πλείων": "πλέων",
            "σμικρός": "μικρός",
            "ξύν": "σύν",
            "τέσσαρες": "τέτταρες",
        }
    
    def _build_dictionary(self):
        """Erstellt das vollständige Wörterbuch aus dem Omega-Wortschatz"""
        
        # ============ ALPHA ============
        self.vocab_dict.update({
            "ἀγαθός": ("gut, anständig", "ἀγαθός, ή, όν", 
                      "3 Steigerungsreihen: 1) ἀμείνων/ἄμεινον, ἄριστος; 2) κρείττων/κρεῖττον, κράτιστος; 3) βελτίων/βέλτιον, βέλτιστος. τὸ ἀγαθόν - das Gute; τὰ ἀγαθά - die Güter"),
            "ἀγανακτέω": ("sich ärgern, unwillig sein", "ἀγανακτέω", ""),
            "ἀγγέλλω": ("melden, berichten", "ἀγγέλλω, ἀγγελῶ, ἤγγειλα, ἤγγελκα, ἤγγελμαι, ἤγγελθην", ""),
            "ἄγγελος": ("Bote", "ἄγγελος, ου, ὁ", ""),
            "ἀγνοέω": ("nicht wissen, nicht kennen", "ἀγνοέω", ""),
            "ἀγορά": ("Marktplatz, Versammlung", "ἀγορά, ᾶς, ἡ", ""),
            "ἀγρός": ("Acker, Feld", "ἀγρός, οῦ, ὁ", ""),
            "ἄγω": ("führen, treiben; ziehen, marschieren", "ἄγω, ἄξω, ἤγαγον, ἦχα, ἤγμαι, ἤχθην", ""),
            "ἀγών": ("Wettkampf, Kampf; Prozess", "ἀγών, ῶνος, ὁ", ""),
            "ἀδελφός": ("Bruder", "ἀδελφός, οῦ, ὁ", ""),
            "ἀδικέω": ("Unrecht tun", "ἀδικέω, ἀδικήσω, ἠδίκησα, ἠδίκηκα, ἠδίκημαι, ἠδικήθην", ""),
            "ἀδικία": ("Unrecht, Ungerechtigkeit", "ἀδικία, ας, ἡ", ""),
            "ἄδικος": ("ungerecht, unrecht", "ἄδικος, ον", ""),
            "ἀδύνατος": ("unfähig, machtlos; unmöglich", "ἀδύνατος, ον", ""),
            "ᾄδω": ("singen, besingen", "ᾄδω", ""),
            "ἀεί": ("immer; jeweils", "ἀεί", ""),
            "ἀθάνατος": ("unsterblich", "ἀθάνατος, ον", ""),
            "ἄθλιος": ("elend, unglücklich", "ἄθλιος, α, ον", ""),
            "ἄθλος": ("Wettkampf; Mühe", "ἄθλος, ου, ὁ", ""),
            "αἰδέομαι": ("scheuen, Ehrfurcht haben; respektieren", "αἰδέομαι, αἰδέσομαι, ἠδέσθην", ""),
            "αἰδώς": ("Scham; Ehrfurcht", "αἰδώς, όος, ἡ", ""),
            "αἱρέω": ("nehmen, ergreifen; zu Fall bringen; M. sich nehmen, wählen", "αἱρέω, αἱρήσω, εἷλον, ᾕρηκα, ᾕρημαι, ἡρέθην", ""),
            "αἴρω": ("hochheben, aufheben; absegeln, aufbrechen", "αἴρω, ἀρῶ, ἦρα, ἦρκα, ἦρμαι, ἦρθην", ""),
            "αἰσθάνομαι": ("wahrnehmen, merken", "αἰσθάνομαι, αἰσθήσομαι, ᾐσθόμην, ᾔσθημαι", ""),
            "αἰσχρός": ("hässlich; schändlich", "αἰσχρός, ά, όν", ""),
            "αἰσχύνομαι": ("sich schämen; respektieren", "αἰσχύνομαι, αἰσχυνοῦμαι, ᾐσχύνθην, ᾔσχυμμαι", ""),
            "αἰτέω": ("fordern, verlangen", "αἰτέω, αἰτήσω, ᾔτησα, ᾔτηκα, ᾔτημαι, ᾐτήθην", ""),
            "αἰτία": ("Grund, Ursache; Schuld", "αἰτία, ας, ἡ", ""),
            "αἴτιος": ("schuld, schuldig; Urheber", "αἴτιος, α, ον", ""),
            "ἀκοή": ("Gehör; Gerücht", "ἀκοή, ῆς, ἡ", ""),
            "ἀκολουθέω": ("folgen", "ἀκολουθέω", ""),
            "ἀκούω": ("hören", "ἀκούω, ἀκούσομαι, ἤκουσα, ἀκήκοα, ἠκούσθην", ""),
            "ἀκριβής": ("sorgfältig, genau", "ἀκριβής, ές", ""),
            "ἄκων": ("unfreiwillig, ungern", "ἄκων, ἄκουσα, ἄκον", ""),
            "ἀλήθεια": ("Wahrheit", "ἀλήθεια, ας, ἡ", ""),
            "ἀληθής": ("wahr, wahrhaftig", "ἀληθής, ές", ""),
            "ἀλίσκομαι": ("gefangen werden; überführt werden", "ἀλίσκομαι, ἁλώσομαι, ἑάλων, ἑάλωκα", ""),
            "ἀλλά": ("aber; sondern", "ἀλλά", ""),
            "ἀλλήλων": ("einander, gegenseitig", "ἀλλήλων, -οις/-αις, -ους/-ας/-α", ""),
            "ἄλλος": ("ein anderer", "ἄλλος, η, ο", ""),
            "ἅμα": ("zugleich; zusammen mit; während", "ἅμα", ""),
            "ἀμαθής": ("ungebildet, unwissend", "ἀμαθής, ές", ""),
            "ἁμαρτάνω": ("verfehlen, falsch machen; sündigen", "ἁμαρτάνω, ἁμαρτήσομαι, ἥμαρτον, ἡμάρτηκα, ἡμάρτημαι, ἡμαρτήθην", ""),
            "ἁμαρτία": ("Fehler, Verfehlung", "ἁμαρτία, ας, ἡ", ""),
            "ἀμελέω": ("sich nicht kümmern; vernachlässigen", "ἀμελέω", ""),
            "ἀμύνω": ("abwehren, fernhalten; helfen; M. sich verteidigen", "ἀμύνω, ἀμυνῶ, ἤμυνα", ""),
            "ἀμφί": ("um...herum", "ἀμφί", ""),
            "ἀμφισβητέω": ("bestreiten, sich streiten; behaupten", "ἀμφισβητέω", ""),
            "ἀμφότεροι": ("beide", "ἀμφότεροι, αι, α", ""),
            "ἄν": ("Modalpartikel", "ἄν", "Potentialis (Optativ), Irrealis (Ind. Impf./Aor.), Iterativ/Eventualis (Konjunktiv)"),
            "ἀνά": ("über...hin; hinauf; während", "ἀνά", ""),
            "ἀναγιγνώσκω": ("lesen, vorlesen", "ἀναγιγνώσκω", ""),
            "ἀναγκάζω": ("zwingen", "ἀναγκάζω", ""),
            "ἀναγκαῖος": ("notwendig", "ἀναγκαῖος, α, ον", ""),
            "ἀνάγκη": ("Notwendigkeit, Zwang", "ἀνάγκη, ης, ἡ", ""),
            "ἀναλαμβάνω": ("aufnehmen", "ἀναλαμβάνω", ""),
            "ἀναμιμνήσκω": ("erinnern; M. sich erinnern", "ἀναμιμνήσκω", ""),
            "ἀνδρεία": ("Tapferkeit", "ἀνδρεία, ας, ἡ", ""),
            "ἀνδρεῖος": ("tapfer", "ἀνδρεῖος, α, ον", ""),
            "ἄνευ": ("ohne", "ἄνευ", ""),
            "ἀνήρ": ("Mann", "ἀνήρ, ἀνδρός, ὁ", ""),
            "ἀνθρώπειος": ("menschlich", "ἀνθρώπειος, α, ον", ""),
            "ἄνθρωπος": ("Mensch", "ἄνθρωπος, ου, ὁ", ""),
            "ἀνίημι": ("loslassen; nachlassen", "ἀνίημι", ""),
            "ἀνίστημι": ("aufstellen; M. aufstehen, sich erheben", "ἀνίστημι", ""),
            "ἀνόητος": ("unvernünftig", "ἀνόητος, ον", ""),
            "ἀνόσιος": ("gottlos; unrecht", "ἀνόσιος, α, ον", ""),
            "ἀντί": ("anstelle von", "ἀντί", ""),
            "ἄξιος": ("würdig, wert; angemessen, richtig", "ἄξιος, ία, ιον", ""),
            "ἀξιόω": ("für würdig halten; fordern; glauben", "ἀξιόω, ἀξιώσω, ἠξίωσα, ἠξίωκα, ἠξίωμαι, ἠξιώθην", ""),
            "ἀπαλλάττω": ("entfernen; befreien", "ἀπαλλάττω, ἀπαλλάξω, ἀπήλλαξα, ἀπήλλαχα, ἀπήλλαγμαι, ἀπηλλάχθην", ""),
            "ἅπας": ("all, ganz, jeder", "ἅπας, ἅπασα, ἅπαν", ""),
            "ἄπειμι": ("weggehen", "ἄπειμι", ""),
            "ἀπιστέω": ("nicht glauben; misstrauen", "ἀπιστέω", ""),
            "ἀπό": ("von, seit", "ἀπό", ""),
            "ἀποδείκνυμι": ("zeigen, darlegen, beweisen", "ἀποδείκνυμι", ""),
            "ἀποδέχομαι": ("annehmen; aufnehmen", "ἀποδέχομαι", ""),
            "ἀποδιδράσκω": ("weglaufen, entlaufen", "ἀποδιδράσκω", ""),
            "ἀποθνῄσκω": ("sterben; tot sein", "ἀποθνῄσκω, ἀποθανοῦμαι, ἀπέθανον, τέθνηκα", ""),
            "ἀποκρίνομαι": ("antworten", "ἀποκρίνομαι, ἀποκρινοῦμαι, ἀπεκρινάμην, ἀπεκρίθην", ""),
            "ἀπόκρισις": ("Antwort", "ἀπόκρισις, εως, ἡ", ""),
            "ἀποκτείνω": ("töten", "ἀποκτείνω, ἀποκτενῶ, ἀπέκτεινα, ἀπέκτονα", ""),
            "ἀπόλλυμι": ("zugrunde richten; verlieren", "ἀπόλλυμι, ἀπολῶ, ἀπώλεσα", "Aor. M. ἀπωλόμην, Perf. ἀπολώλεκα/ἀπόλωλα"),
            "ἀπολογέομαι": ("sich verteidigen", "ἀπολογέομαι", ""),
            "ἀπορία": ("Ratlosigkeit; Mangel", "ἀπορία, ας, ἡ", ""),
            "ἀποφαίνω": ("zeigen, darlegen", "ἀποφαίνω", ""),
            "ἅπτομαι": ("berühren, anfassen; sich befassen mit", "ἅπτομαι, ἅψομαι, ἡψάμην, ἧμμαι, ἥφθην", ""),
            "ἄρα": ("also, folglich", "ἄρα", ""),
            "ἆρα": ("Fragepartikel", "ἆρα", ""),
            "ἀργύριον": ("Silber, Geld", "ἀργύριον, ου, τό", ""),
            "ἀρετή": ("Tüchtigkeit, Tugend; Tapferkeit; Leistung", "ἀρετή, ῆς, ἡ", ""),
            "ἀριθμός": ("Zahl", "ἀριθμός, οῦ, ὁ", ""),
            "ἄριστος": ("der beste, tüchtigste", "ἄριστος, η, ον", "Superlativ von ἀγαθός"),
            "ἀρκέω": ("stark genug sein, genügen", "ἀρκέω", ""),
            "ἀρχαῖος": ("alt, früher", "ἀρχαῖος, α, ον", ""),
            "ἀρχή": ("Anfang; Herrschaft, Reich; Amt", "ἀρχή, ῆς, ἡ", ""),
            "ἄρχομαι": ("anfangen", "ἄρχομαι, ἄρξομαι, ἠρξάμην", ""),
            "ἄρχω": ("herrschen; den Anfang machen", "ἄρχω, ἄρξω, ἦρξα, ἦργμαι, ἦρχθην", ""),
            "ἄρχων": ("Herrscher, Anführer; Archont", "ἄρχων, οντος, ὁ", ""),
            "ἀσθενής": ("schwach, kraftlos; krank", "ἀσθενής, ές", ""),
            "ἀσκέω": ("üben, ausüben", "ἀσκέω", ""),
            "ἄστρον": ("Stern", "ἄστρον, ου, τό", ""),
            "ἄτε": ("da, weil", "ἄτε", "objektiver Grund im Unterschied zu ὡς + Part."),
            "ἄτοπος": ("unpassend, seltsam", "ἄτοπος, ον", ""),
            "αὖ": ("wieder; wiederum", "αὖ, αὖθις", ""),
            "αὐτίκα": ("sofort", "αὐτίκα", ""),
            "αὐτός": ("selbst; derselbe", "αὐτός, ή, ό", "Personalpronomen der 3.Ps."),
            "αὐτοῦ": ("ebendort", "αὐτοῦ", ""),
            "ἀφαιρέω": ("wegnehmen", "ἀφαιρέω, ἀφαιρήσω, ἀφεῖλον, ἀφήρηκα, ἀφήρημαι, ἀφηρέθην", ""),
            "ἀφίημι": ("losschicken; freilassen", "ἀφίημι, ἀφήσω, ἀφῆκα, ἀφεῖκα, ἀφεῖμαι, ἀφείθην", ""),
            "ἀφικνέομαι": ("ankommen", "ἀφικνέομαι, ἀφίξομαι, ἀφικόμην, ἀφῖγμαι", ""),
            "ἄφρων": ("unvernünftig", "ἄφρων, ον", ""),
            "ἄχθομαι": ("unwillig sein, sich ärgern", "ἄχθομαι", ""),
        })
        
        # ============ BETA ============
        self.vocab_dict.update({
            "βαίνω": ("gehen", "βαίνω, βήσομαι, ἔβην, βέβηκα", ""),
            "βάλλω": ("werfen; treffen", "βάλλω, βαλῶ, ἔβαλον, βέβληκα, βέβλημαι, ἐβλήθην", ""),
            "βάρβαρος": ("nichtgriechisch", "βάρβαρος, ον", ""),
            "βασιλεύς": ("König", "βασιλεύς, έως, ὁ", ""),
            "βέβαιος": ("fest, beständig, zuverlässig", "βέβαιος, α, ον", ""),
            "βελτίων": ("besser", "βελτίων, βέλτιον", "Komp. zu ἀγαθός, Superl. βέλτιστος"),
            "βιάζομαι": ("zwingen, überwältigen", "βιάζομαι", ""),
            "βιβλίον": ("Buch", "βιβλίον, ου, τό", ""),
            "βίος": ("Leben; Lebensunterhalt", "βίος, ου, ὁ", ""),
            "βιόω": ("leben", "βιόω, βιώσομαι, ἐβίων, βεβίωκα", ""),
            "βλάπτω": ("schädigen, schaden", "βλάπτω, βλάψω, ἔβλαψα, βέβλαφα, βέβλαμμαι, ἐβλάβην", ""),
            "βλέπω": ("blicken, sehen", "βλέπω, βλέψομαι, ἔβλεψα", ""),
            "βοηθέω": ("helfen", "βοηθέω, βοηθήσω, ἐβοήθησα, βεβοήθηκα", ""),
            "βουλεύω": ("beraten, überlegen; beschließen", "βουλεύω, βουλεύσω, ἐβούλευσα, βεβούλευκα, βεβούλευμαι, ἐβουλεύθην", ""),
            "βουλή": ("Plan, Rat, Absicht; Ratsversammlung", "βουλή, ῆς, ἡ", ""),
            "βούλομαι": ("wollen", "βούλομαι, βουλήσομαι, βεβούλημαι, ἐβουλήθην", ""),
            "βοῦς": ("Rind, Kuh", "βοῦς, βοός, ὁ/ἡ", ""),
            "βροτός": ("sterblich", "βροτός, ή, όν", ""),
        })
        
        # ============ GAMMA ============
        self.vocab_dict.update({
            "γάμος": ("Hochzeit, Ehe", "γάμος, ου, ὁ", ""),
            "γάρ": ("denn, nämlich", "γάρ", ""),
            "γε": ("jedenfalls; wenigstens", "γε", "häufig unübersetzt"),
            "γελάω": ("lachen; auslachen", "γελάω, γελάσομαι, ἐγέλασα", ""),
            "γενναῖος": ("edel, adlig; tüchtig; echt", "γενναῖος, α, ον", ""),
            "γένος": ("Geschlecht, Gattung, Abstammung", "γένος, ους, τό", ""),
            "γέρων": ("alter Mann, Greis", "γέρων, οντος, ὁ", ""),
            "γεωργός": ("Bauer", "γεωργός, οῦ, ὁ", ""),
            "γῆ": ("Erde; Land", "γῆ, γῆς, ἡ", ""),
            "γίγνομαι": ("werden; entstehen; geschehen", "γίγνομαι, γενήσομαι, ἐγενόμην, γέγονα/γεγένημαι", ""),
            "γιγνώσκω": ("erkennen, kennen", "γιγνώσκω, γνώσομαι, ἔγνων, ἔγνωκα, ἔγνωσμαι, ἐγνώσθην", ""),
            "γλυκύς": ("süß, lieb", "γλυκύς, εῖα, ύ", ""),
            "γλῶττα": ("Zunge; Sprache", "γλῶττα, ης, ἡ", ""),
            "γνώμη": ("Verstand, Einsicht; Gesinnung, Meinung", "γνώμη, ης, ἡ", ""),
            "γοῦν": ("jedenfalls, wenigstens", "γοῦν", ""),
            "γράμμα": ("Buchstabe; Schrift; Wissenschaft", "γράμμα, ατος, τό", "τὰ γράμματα - Literatur, Wissenschaften"),
            "γράφω": ("schreiben", "γράφω, γράψω, ἔγραψα, γέγραφα, γέγραμμαι, ἐγράφην", "γραφὴν γράφομαι - anklagen"),
            "γυμνάζω": ("üben, trainieren", "γυμνάζω", ""),
            "γυμνός": ("nackt; unbewaffnet", "γυμνός, ή, όν", ""),
            "γυνή": ("Frau", "γυνή, γυναικός, ἡ", ""),
        })
        
        # ============ DELTA ============
        self.vocab_dict.update({
            "δαιμόνιον": ("göttliches Wesen, göttliche Stimme", "δαιμόνιον, ου, τό", ""),
            "δαίμων": ("Gottheit; Götterwille", "δαίμων, ονος, ὁ/ἡ", ""),
            "δέ": ("aber; und", "δέ", ""),
            "δέδοικα": ("fürchten", "δέδοικα/δέδια, δείσομαι, ἔδεισα", "Perfekt mit Präsensbedeutung"),
            "δεῖ": ("es ist nötig; man muss", "δεῖ, δεήσει, ἔδει", "verneint: man darf nicht"),
            "δείκνυμι": ("zeigen; nachweisen", "δείκνυμι, δείξω, ἔδειξα, δέδειχα, δέδειγμαι, ἐδείχθην", ""),
            "δειλός": ("furchtsam, feige; elend", "δειλός, ή, όν", ""),
            "δεινός": ("gewaltig; furchtbar; tüchtig", "δεινός, ή, όν", ""),
            "δεῖπνον": ("Mahlzeit, Abendessen", "δεῖπνον, ου, τό", ""),
            "δέκα": ("zehn", "δέκα", ""),
            "δένδρον": ("Baum", "δένδρον, ου, τό", ""),
            "δέομαι": ("bedürfen, nötig haben; bitten", "δέομαι, δεήσομαι, ἐδεήθην", "δέομαί τινος τί - jdn. um etw. bitten"),
            "δέον": ("da es nötig ist", "δέον", "τὸ δέον/τὰ δέοντα - das Nötige"),
            "δεσπότης": ("Herr, Herrscher", "δεσπότης, ου, ὁ", ""),
            "δεῦρο": ("hierher", "δεῦρο", ""),
            "δεύτερος": ("der zweite", "δεύτερος, α, ον", ""),
            "δέχομαι": ("annehmen, aufnehmen", "δέχομαι, δέξομαι, ἐδεξάμην, δέδεγμαι, ἐδέχθην", ""),
            "δέω": ("fesseln, binden", "δέω", ""),
            "δή": ("also, wirklich", "δή", "oft zur Verstärkung"),
            "δῆλος": ("offensichtlich, klar", "δῆλος, η, ον", ""),
            "δηλόω": ("klar machen, zeigen", "δηλόω, δηλώσω, ἐδήλωσα, δεδήλωκα, ἐδηλώθην", ""),
            "δημιουργός": ("Handwerker; Schöpfer", "δημιουργός, οῦ, ὁ", ""),
            "δῆμος": ("Gemeinde; Volk", "δῆμος, ου, ὁ", ""),
            "δημόσιος": ("staatlich, öffentlich", "δημόσιος, α, ον", "δημοσίᾳ - öffentlich, Ggs. ἰδίᾳ"),
            "δήπου": ("doch wohl, sicherlich", "δήπου", ""),
            "δῆτα": ("bestimmt, durchaus", "δῆτα", ""),
            "διά": ("durch (+Gen.); wegen (+Akk.)", "διά", "διὰ τί - weshalb; διὰ τοῦτο - deshalb"),
            "διαβάλλω": ("verleumden", "διαβάλλω", ""),
            "διαλέγομαι": ("sich unterhalten", "διαλέγομαι, διαλέξομαι, διελέχθην, διείλεγμαι", ""),
            "διανοέομαι": ("denken, beabsichtigen", "διανοέομαι", ""),
            "διαφέρω": ("sich unterscheiden", "διαφέρω, διοίσω, διήνεγκον, διενήνοχα, διενήνεγμαι", "διαφέρει - es macht einen Unterschied"),
            "διαφθείρω": ("verderben, vernichten", "διαφθείρω, διαφθερῶ, διέφθειρα, διέφθαρκα, διέφθαρμαι, διεφθάρην", ""),
            "διδάσκαλος": ("Lehrer", "διδάσκαλος, ου, ὁ", ""),
            "διδάσκω": ("lehren, unterrichten", "διδάσκω, διδάξω, ἐδίδαξα, δεδίδαχα, δεδίδαγμαι, ἐδιδάχθην", ""),
            "δίδωμι": ("geben", "δίδωμι, δώσω, ἔδωκα, δέδωκα, δέδομαι, ἐδόθην", "δίκην δίδωμι - bestraft werden"),
            "διέρχομαι": ("hindurchgehen; erörtern", "διέρχομαι", ""),
            "δικάζω": ("Recht sprechen, urteilen", "δικάζω", "δικάζομαι - prozessieren"),
            "δίκαιος": ("gerecht, richtig", "δίκαιος, ία, ιον", "δικαιός εἰμι + Inf. - berechtigt sein"),
            "δικαιοσύνη": ("Gerechtigkeit", "δικαιοσύνη, ης, ἡ", ""),
            "δικαιόω": ("für recht halten, fordern", "δικαιόω", ""),
            "δικαστήριον": ("Gericht", "δικαστήριον, ου, τό", ""),
            "δικαστής": ("Richter", "δικαστής, οῦ, ὁ", ""),
            "δίκη": ("Recht, Gerechtigkeit; Prozess, Strafe", "δίκη, ης, ἡ", "δίκην δίδωμι - bestraft werden"),
            "διό": ("deshalb", "διό", ""),
            "διώκω": ("verfolgen; anklagen", "διώκω, διώξομαι, ἐδίωξα, δεδίωχα, δεδίωγμαι, ἐδιώχθην", ""),
            "δοκέω": ("scheinen; meinen, glauben", "δοκέω, δόξω, ἔδοξα", "δοκεῖ μοι - ich beschließe"),
            "δόξα": ("Meinung; Schein; Ruf", "δόξα, ης, ἡ", ""),
            "δοξάζω": ("meinen", "δοξάζω", ""),
            "δοῦλος": ("Sklave, Knecht", "δοῦλος, ου, ὁ", ""),
            "δράω": ("tun, handeln", "δράω, δράσω, ἔδρασα, δέδρακα, δέδραμαι, ἐδράσθην", ""),
            "δύναμαι": ("können, vermögen; bedeuten", "δύναμαι, δυνήσομαι, ἐδυνήθην, δεδύνημαι", ""),
            "δύναμις": ("Kraft, Macht, Fähigkeit", "δύναμις, εως, ἡ", ""),
            "δυνατός": ("fähig; mächtig; möglich", "δυνατός, ή, όν", ""),
            "δύο": ("zwei", "δύο", ""),
            "δῶρον": ("Geschenk, Gabe", "δῶρον, ου, τό", ""),
        })
        
        # ============ EPSILON ============
        self.vocab_dict.update({
            "ἐάν": ("wenn; immer wenn", "ἐάν", ""),
            "ἑαυτοῦ": ("seiner/ihrer selbst, sich", "ἑαυτοῦ, ἑαυτῆς, ἑαυτοῦ", "Reflexivpronomen der 3.Ps."),
            "ἐάω": ("lassen, zulassen", "ἐάω, ἐάσω, εἴασα", ""),
            "ἐγώ": ("ich", "ἐγώ, ἐμοῦ", ""),
            "ἐθέλω": ("wollen; bereit sein", "ἐθέλω, ἐθελήσω, ἠθέλησα, ἠθέληκα", ""),
            "ἔθνος": ("Volk, Volksstamm", "ἔθνος, ους, τό", ""),
            "ἔθος": ("Sitte; Gewohnheit", "ἔθος, ους, τό", ""),
            "εἰ": ("wenn, falls; ob", "εἰ", ""),
            "εἰ γάρ": ("wenn doch, hoffentlich", "εἰ γάρ", ""),
            "εἶδος": ("Gestalt, Aussehen; Idee", "εἶδος, ους, τό", ""),
            "εἴδωλον": ("Bild, Götterbild", "εἴδωλον, ου, τό", ""),
            "εἶεν": ("nun gut", "εἶεν", ""),
            "εἶθε": ("wenn doch, hoffentlich", "εἶθε", ""),
            "εἰκός": ("Wahrscheinlichkeit; Angemessenheit", "εἰκός, ότος, τό", "εἰκός ἐστι - es ist wahrscheinlich/angemessen"),
            "εἰκών": ("Bild; Statue", "εἰκών, όνος, ἡ", ""),
            "εἰμί": ("sein", "εἰμί, ἔσομαι, ἦν", "ἔστιν - es gibt, es ist möglich"),
            "εἶμι": ("gehen", "εἶμι", "Futur zu ἔρχομαι"),
            "εἶπερ": ("wenn wirklich", "εἶπερ", ""),
            "εἰρήνη": ("Friede", "εἰρήνη, ης, ἡ", ""),
            "εἷς": ("einer", "εἷς, μία, ἕν", ""),
            "εἰς": ("in...hinein; zu...hin", "εἰς", ""),
            "εἶτα": ("da, dann; ferner", "εἶτα", ""),
            "εἴτε...εἴτε": ("sei es... sei es", "εἴτε...εἴτε", ""),
            "εἴωθα": ("gewohnt sein", "εἴωθα", "Perfekt mit Präsensbedeutung"),
            "ἐκ": ("aus; seit; infolge von", "ἐκ, ἐξ", ""),
            "ἕκαστος": ("jeder", "ἕκαστος, ἑκάστη, ἕκαστον", ""),
            "ἑκάστοτε": ("jedesmal", "ἑκάστοτε", ""),
            "ἑκάτερος": ("jeder von beiden", "ἑκάτερος, ἑκατέρα, ἑκάτερον", ""),
            "ἑκατόν": ("hundert", "ἑκατόν", ""),
            "ἐκβάλλω": ("hinauswerfen, vertreiben", "ἐκβάλλω, ἐκβαλῶ, ἐξέβαλον, ἐκβέβληκα, ἐκβέβλημαι, ἐξεβλήθην", ""),
            "ἐκεῖ": ("dort", "ἐκεῖ", ""),
            "ἐκεῖνος": ("jener", "ἐκεῖνος, η, ο", ""),
            "ἐκκλησία": ("Volksversammlung; Kirche", "ἐκκλησία, ας, ἡ", ""),
            "ἐκπλήττω": ("erschrecken", "ἐκπλήττω", ""),
            "ἑκών": ("freiwillig, willentlich", "ἑκών, ἑκοῦσα, ἑκόν", ""),
            "ἐλάττων": ("kleiner, geringer", "ἐλάττων, ον", "Komp. zu μικρός/ὀλίγος"),
            "ἐλαύνω": ("treiben, marschieren", "ἐλαύνω, ἐλῶ, ἤλασα, ἐλήλακα, ἐλήλαμαι, ἠλάθην", ""),
            "ἐλέγχω": ("prüfen; widerlegen", "ἐλέγχω", ""),
            "ἐλευθερία": ("Freiheit", "ἐλευθερία, ας, ἡ", ""),
            "ἐλεύθερος": ("frei", "ἐλεύθερος, α, ον", ""),
            "ἐλπίζω": ("hoffen, erwarten", "ἐλπίζω", ""),
            "ἐλπίς": ("Hoffnung, Erwartung", "ἐλπίς, ίδος, ἡ", ""),
            "ἐμαυτοῦ": ("meiner selbst", "ἐμαυτοῦ, ῆς, οῦ", "Reflexivpronomen 1.Ps."),
            "ἐμός": ("mein", "ἐμός, ή, όν", ""),
            "ἔμπειρος": ("erfahren, kundig", "ἔμπειρος, ον", ""),
            "ἐμπίπτω": ("hineinfallen, geraten in", "ἐμπίπτω", ""),
            "ἔμπροσθεν": ("vorne; früher", "ἔμπροσθεν", ""),
            "ἐν": ("in, an, auf, bei; während", "ἐν", ""),
            "ἐν ᾧ": ("während", "ἐν ᾧ", ""),
            "ἐναντίος": ("gegenüber; entgegengesetzt", "ἐναντίος, α, ον", "ὁ ἐναντίος - Gegner"),
            "ἔνεκα": ("wegen; um...willen", "ἔνεκα", ""),
            "ἔνθα": ("da, dort", "ἔνθα", ""),
            "ἐνθάδε": ("hier", "ἐνθάδε", ""),
            "ἐνθυμέομαι": ("bedenken, überlegen", "ἐνθυμέομαι", ""),
            "ἔνιοι": ("einige", "ἔνιοι, αι, α", ""),
            "ἐνίοτε": ("manchmal", "ἐνίοτε", ""),
            "ἐννοέω": ("bedenken; begreifen", "ἐννοέω", ""),
            "ἐνταῦθα": ("hier; dort", "ἐνταῦθα", ""),
            "ἐντυγχάνω": ("treffen auf, geraten in", "ἐντυγχάνω, ἐντεύξομαι, ἐνέτυχον, ἐντετύχηκα", ""),
            "ἕξ": ("sechs", "ἕξ", ""),
            "ἐξ οὗ": ("seitdem", "ἐξ οὗ", ""),
            "ἔξεστι": ("es ist möglich; es ist erlaubt", "ἔξεστι", ""),
            "ἐξετάζω": ("untersuchen, prüfen", "ἐξετάζω", ""),
            "ἔοικα": ("scheinen; gleichen", "ἔοικα", "Perfekt mit Präsensbedeutung"),
            "ἐπαγγέλλομαι": ("ankündigen; angeben", "ἐπαγγέλλομαι", ""),
            "ἐπαινέω": ("loben", "ἐπαινέω", ""),
            "ἔπαινος": ("Lob", "ἔπαινος, ου, ὁ", ""),
            "ἐπεί": ("als, nachdem; da, weil", "ἐπεί", ""),
            "ἐπειδή": ("als, nachdem; da, weil", "ἐπειδή", ""),
            "ἔπειμι": ("hingehen; angreifen", "ἔπειμι", ""),
            "ἔπειτα": ("dann, darauf", "ἔπειτα", ""),
            "ἐπί": ("auf (+Gen.); bei (+Dat.); zu (+Akk.)", "ἐπί", ""),
            "ἐπιβουλεύω": ("einen Anschlag planen", "ἐπιβουλεύω", ""),
            "ἐπιδείκνυμι": ("vorzeigen, zur Schau stellen", "ἐπιδείκνυμι", ""),
            "ἐπιθυμέω": ("begehren, wollen", "ἐπιθυμέω", ""),
            "ἐπιθυμία": ("Begierde, Verlangen", "ἐπιθυμία, ας, ἡ", ""),
            "ἐπιλανθάνομαι": ("vergessen", "ἐπιλανθάνομαι, ἐπιλήσομαι, ἐπελαθόμην, ἐπιλέλησμαι", ""),
            "ἐπιμέλεια": ("Sorge, Fürsorge", "ἐπιμέλεια, ας, ἡ", ""),
            "ἐπιμελέομαι": ("sich kümmern", "ἐπιμελέομαι", ""),
            "ἐπίσταμαι": ("verstehen; wissen; können", "ἐπίσταμαι", ""),
            "ἐπιστήμη": ("Wissen, Wissenschaft", "ἐπιστήμη, ης, ἡ", ""),
            "ἐπιστολή": ("Brief", "ἐπιστολή, ῆς, ἡ", ""),
            "ἐπιτήδειος": ("geeignet, passend", "ἐπιτήδειος, ον", "τὰ ἐπιτήδεια - Lebensmittel"),
            "ἐπιτίθημι": ("darauflegen; zufügen", "ἐπιτίθημι", ""),
            "ἐπιτρέπω": ("überlassen; gestatten", "ἐπιτρέπω", ""),
            "ἐπιχειρέω": ("versuchen; angreifen", "ἐπιχειρέω", ""),
            "ἕπομαι": ("folgen", "ἕπομαι, ἕψομαι, ἑσπόμην", ""),
            "ἔπος": ("Wort", "ἔπος, ους, τό", ""),
            "ἐράω": ("lieben, begehren", "ἐράω", ""),
            "ἐργάζομαι": ("arbeiten, tun", "ἐργάζομαι, ἐργάσομαι, εἰργασάμην, εἴργασμαι", ""),
            "ἔργον": ("Werk, Arbeit; Tat", "ἔργον, ου, τό", ""),
            "ἔρημος": ("einsam, verlassen", "ἔρημος, η, ον", ""),
            "ἔρις": ("Streit, Zank", "ἔρις, ιδος, ἡ", ""),
            "ἔρχομαι": ("gehen, kommen", "ἔρχομαι, εἶμι, ἦλθον, ἐλήλυθα", ""),
            "ἔρως": ("Liebe, Verlangen", "ἔρως, ωτος, ὁ", ""),
            "ἐρωτάω": ("fragen", "ἐρωτάω, ἐρήσομαι, ἠρόμην", ""),
            "ἐσθίω": ("essen", "ἐσθίω", ""),
            "ἑσπέρα": ("Abend", "ἑσπέρα, ας, ἡ", ""),
            "ἔσχατος": ("letzter, äußerster", "ἔσχατος, η, ον", ""),
            "ἑταῖρος": ("Freund, Gefährte", "ἑταῖρος, ου, ὁ", ""),
            "ἕτερος": ("der andere", "ἕτερος, α, ον", ""),
            "ἔτι": ("noch", "ἔτι", ""),
            "ἕτοιμος": ("bereit", "ἕτοιμος, η, ον", ""),
            "ἔτος": ("Jahr", "ἔτος, ους, τό", ""),
            "εὖ": ("gut", "εὖ", ""),
            "εὐδαιμονία": ("Glück, Glückseligkeit", "εὐδαιμονία, ας, ἡ", ""),
            "εὐδαίμων": ("glücklich, selig", "εὐδαίμων, ον", ""),
            "εὐθύς": ("sofort", "εὐθύς", ""),
            "εὑρίσκω": ("finden, erfinden", "εὑρίσκω, εὑρήσω, ηὗρον/εὗρον, ηὕρηκα/εὕρηκα", ""),
            "εὐχή": ("Gebet, Bitte", "εὐχή, ῆς, ἡ", ""),
            "εὔχομαι": ("beten; erflehen", "εὔχομαι", ""),
            "ἐφίστημι": ("voranstellen", "ἐφίστημι", ""),
            "ἐχθρός": ("feindlich, verhasst", "ἐχθρός, ά, όν", "ὁ ἐχθρός - der Feind"),
            "ἔχω": ("haben, halten; können", "ἔχω, ἕξω/σχήσω, ἔσχον, ἔσχηκα", "εὖ ἔχω - es geht mir gut"),
        })
        
        # ============ ZETA ============
        self.vocab_dict.update({
            "Ζεύς": ("Zeus", "Ζεύς, Διός, ὁ", "νὴ Δία/μὰ Δία - bei Zeus!"),
            "ζηλόω": ("nacheifern, bewundern", "ζηλόω", ""),
            "ζημία": ("Strafe", "ζημία, ας, ἡ", ""),
            "ζητέω": ("suchen; untersuchen; streben", "ζητέω, ζητήσω, ἐζήτησα, ἐζήτηκα", ""),
            "ζήτησις": ("Untersuchung", "ζήτησις, εως, ἡ", ""),
            "ζάω": ("leben", "ζάω, ζήσω, ἔζησα, ἔζηκα", ""),
            "ζωή": ("Leben", "ζωή, ῆς, ἡ", ""),
            "ζῷον": ("Lebewesen; Tier", "ζῷον, ου, τό", ""),
        })
        
        # ============ ETA ============
        self.vocab_dict.update({
            "ἤ": ("oder; als", "ἤ", ""),
            "ἡγεμών": ("Führer, Anführer", "ἡγεμών, όνος, ὁ", ""),
            "ἡγέομαι": ("führen; glauben, meinen", "ἡγέομαι, ἡγήσομαι, ἡγησάμην", ""),
            "ἤδη": ("schon", "ἤδη", ""),
            "ἥδομαι": ("sich freuen", "ἥδομαι", ""),
            "ἡδονή": ("Vergnügen, Lust", "ἡδονή, ῆς, ἡ", ""),
            "ἡδύς": ("süß, angenehm", "ἡδύς, εῖα, ύ", ""),
            "ἦθος": ("Charakter, Wesensart", "ἦθος, ους, τό", ""),
            "ἥκω": ("kommen, da sein", "ἥκω, ἥξω", ""),
            "ἡλικία": ("Lebensalter", "ἡλικία, ας, ἡ", ""),
            "ἥλιος": ("Sonne", "ἥλιος, ου, ὁ", ""),
            "ἡμεῖς": ("wir", "ἡμεῖς, ἡμῶν, ἡμῖν, ἡμᾶς", ""),
            "ἡμέρα": ("Tag", "ἡμέρα, ας, ἡ", ""),
            "ἡμέτερος": ("unser", "ἡμέτερος, α, ον", ""),
            "ἥρως": ("Held, Halbgott", "ἥρως, ωος, ὁ", ""),
            "ἡσυχία": ("Ruhe", "ἡσυχία, ας, ἡ", "ἡσυχίαν ἄγω - Ruhe bewahren"),
            "ἥττων": ("geringer, schwächer", "ἥττων, ἧττον", "οὐδὲν ἧττον - trotzdem"),
        })
        
        # ============ THETA ============
        self.vocab_dict.update({
            "θάλαττα": ("Meer", "θάλαττα, ης, ἡ", ""),
            "θάνατος": ("Tod", "θάνατος, ου, ὁ", ""),
            "θάπτω": ("bestatten, begraben", "θάπτω", ""),
            "θαρρέω": ("kühn sein, mutig sein", "θαρρέω", ""),
            "θαυμάζω": ("staunen, bewundern", "θαυμάζω, θαυμάσομαι, ἐθαύμασα, τεθαύμακα", ""),
            "θαυμάσιος": ("erstaunlich, wunderbar", "θαυμάσιος, α, ον", ""),
            "θεάομαι": ("betrachten, anschauen", "θεάομαι, θεάσομαι, ἐθεασάμην, τεθέαμαι", ""),
            "θέατρον": ("Theater", "θέατρον, ου, τό", ""),
            "θεῖος": ("göttlich", "θεῖος, θεία, θεῖον", ""),
            "θεός": ("Gott, Göttin", "θεός, οῦ, ὁ/ἡ", ""),
            "θεραπεύω": ("verehren; pflegen", "θεραπεύω", ""),
            "θερμός": ("warm", "θερμός, ή, όν", ""),
            "θεωρέω": ("betrachten, zuschauen", "θεωρέω", ""),
            "θηράω": ("jagen, erjagen", "θηράω", ""),
            "θησαυρός": ("Schatzkammer, Schatz", "θησαυρός, οῦ, ὁ", ""),
            "θνητός": ("sterblich", "θνητός, ή, όν", ""),
            "θρόνος": ("Sessel, Thron", "θρόνος, ου, ὁ", ""),
            "θυγάτηρ": ("Tochter", "θυγάτηρ, τρός, ἡ", ""),
            "θυμός": ("Mut, Zorn; Herz, Gemüt", "θυμός, οῦ, ὁ", ""),
            "θύρα": ("Tür, Tor", "θύρα, ας, ἡ", ""),
            "θύω": ("opfern", "θύω, θύσω, ἔθυσα, τέθυκα", ""),
        })
        
        # ============ IOTA ============
        self.vocab_dict.update({
            "ἰατρική": ("Heilkunst", "ἰατρική, ῆς, ἡ", ""),
            "ἰατρός": ("Arzt", "ἰατρός, οῦ, ὁ", ""),
            "ἴδιος": ("eigen; privat", "ἴδιος, ία, ιον", "ἰδίᾳ - privat"),
            "ἰδιώτης": ("Privatmann, Laie", "ἰδιώτης, ου, ὁ", ""),
            "ἱερός": ("heilig, geweiht", "ἱερός, ά, όν", ""),
            "ἵημι": ("in Bewegung setzen", "ἵημι, ἥσω, ἧκα, εἷκα, εἷμαι, εἵθην", ""),
            "ἱκανός": ("ausreichend; geeignet", "ἱκανός, ή, όν", ""),
            "ἱκετεύω": ("anflehen", "ἱκετεύω", ""),
            "ἵνα": ("damit, um zu; wo", "ἵνα", ""),
            "ἵππος": ("Pferd", "ἵππος, ου, ὁ", ""),
            "ἴσος": ("gleich; gerecht", "ἴσος, η, ον", ""),
            "ἵστημι": ("stellen, hinstellen", "ἵστημι, στήσω, ἔστησα/ἔστην, ἔστηκα", ""),
            "ἰστορία": ("Forschung, Geschichte", "ἰστορία, ας, ἡ", ""),
            "ἰσχυρός": ("stark, kraftvoll", "ἰσχυρός, ά, όν", ""),
            "ἴσως": ("vielleicht", "ἴσως", ""),
        })
        
        # ============ KAPPA ============
        self.vocab_dict.update({
            "καθεύδω": ("schlafen", "καθεύδω", ""),
            "κάθημαι": ("sitzen", "κάθημαι", ""),
            "καί": ("und; auch, sogar", "καί", "καί...καί - sowohl...als auch, καὶ δὴ καί - und ganz besonders"),
            "καίπερ": ("obwohl", "καίπερ", ""),
            "καιρός": ("rechte Zeit, Gelegenheit", "καιρός, οῦ, ὁ", "κατὰ καιρόν - zur rechten Zeit"),
            "καίτοι": ("und doch", "καίτοι", ""),
            "καίω": ("anzünden, verbrennen", "καίω", ""),
            "κακός": ("schlecht, böse", "κακός, ή, όν", "κακῶς λέγω - schlecht reden"),
            "καλέω": ("rufen; nennen", "καλέω, καλῶ, ἐκάλεσα, κέκληκα, κέκλημαι, ἐκλήθην", "ὁ καλούμενος - der sogenannte"),
            "καλός": ("schön, gut", "καλός, ή, όν", ""),
            "καρδία": ("Herz", "καρδία, ας, ἡ", ""),
            "κατά": ("von...herab (+Gen.); gemäß (+Akk.)", "κατά", "κατὰ φύσιν - gemäß der Natur"),
            "κατανοέω": ("wahrnehmen, verstehen", "κατανοέω", ""),
            "κατασκευάζω": ("einrichten", "κατασκευάζω", ""),
            "καταφρονέω": ("verachten", "καταφρονέω", ""),
            "κατέχω": ("niederhalten, festhalten", "κατέχω", ""),
            "κατηγορέω": ("anklagen", "κατηγορέω", ""),
            "κεῖμαι": ("liegen", "κεῖμαι, κείσομαι", ""),
            "κελεύω": ("befehlen, auffordern", "κελεύω, κελεύσω, ἐκέλευσα", ""),
            "κερδαίνω": ("gewinnen", "κερδαίνω", ""),
            "κέρδος": ("Gewinn, Vorteil", "κέρδος, ους, τό", ""),
            "κεφαλή": ("Kopf", "κεφαλή, ῆς, ἡ", ""),
            "κινδυνεύω": ("in Gefahr sein; scheinen", "κινδυνεύω", ""),
            "κίνδυνος": ("Gefahr", "κίνδυνος, ου, ὁ", ""),
            "κινέω": ("bewegen", "κινέω", ""),
            "κλέπτω": ("stehlen", "κλέπτω", ""),
            "κοινός": ("gemeinsam", "κοινός, ή, όν", "κοινῇ - gemeinsam"),
            "κολάζω": ("bestrafen", "κολάζω", ""),
            "κομίζω": ("bringen, transportieren", "κομίζω", ""),
            "κόρη": ("Mädchen, Tochter", "κόρη, ης, ἡ", ""),
            "κοσμέω": ("ordnen, schmücken", "κοσμέω", ""),
            "κόσμος": ("Ordnung; Schmuck; Welt", "κόσμος, ου, ὁ", ""),
            "κρατέω": ("stärker sein; besiegen", "κρατέω, κρατήσω, ἐκράτησα", ""),
            "κράτος": ("Stärke, Macht", "κράτος, ους, τό", ""),
            "κρείττων": ("stärker, besser", "κρείττων, κρεῖττον", "Komp. zu ἀγαθός"),
            "κρίνω": ("unterscheiden; urteilen", "κρίνω, κρινῶ, ἔκρινα, κέκρικα", ""),
            "κρίσις": ("Entscheidung, Urteil", "κρίσις, εως, ἡ", ""),
            "κρύπτω": ("verbergen", "κρύπτω", ""),
            "κτάομαι": ("erwerben", "κτάομαι, κτήσομαι, ἐκτησάμην, κέκτημαι", "κέκτημαι - besitzen"),
            "κτῆμα": ("Besitz", "κτῆμα, ατος, τό", ""),
            "κύκλος": ("Kreis", "κύκλος, ου, ὁ", ""),
            "κύριος": ("Herr", "κύριος, ου, ὁ", ""),
            "κωλύω": ("hindern, abhalten", "κωλύω, κωλύσω, ἐκώλυσα", ""),
        })
        
        # ============ LAMDA ============
        self.vocab_dict.update({
            "λαμβάνω": ("nehmen, ergreifen; erhalten", "λαμβάνω, λήψομαι, ἔλαβον, εἴληφα, εἴλημμαι, ἐλήφθην", ""),
            "λανθάνω": ("verborgen sein", "λανθάνω, λήσω, ἔλαθον, λέληθα", "λανθάνω ποιῶν τι - etw. unbemerkt tun"),
            "λέγω": ("sagen, sprechen; nennen", "λέγω, ἐρῶ, εἶπον, εἴρηκα, εἴρημαι, ἐλέχθην/ἐρρήθην", "ὡς ἔπος εἰπεῖν - sozusagen"),
            "λείπω": ("lassen; verlassen", "λείπω, λείψω, ἔλιπον, λέλοιπα, λέλειμμαι, ἐλείφθην", ""),
            "λίθος": ("Stein", "λίθος, ου, ὁ", ""),
            "λογίζομαι": ("rechnen, überlegen", "λογίζομαι, λογιοῦμαι, ἐλογισάμην, λελόγισμαι", ""),
            "λόγος": ("Wort, Rede; Gedanke; Erzählung", "λόγος, ου, ὁ", "λόγον δίδωμι - Rechenschaft ablegen"),
            "λοιπός": ("übrig", "λοιπός, ή, όν", "τὸ λοιπόν - künftig"),
            "λυπέω": ("betrüben", "λυπέω", ""),
            "λύπη": ("Schmerz, Leid", "λύπη, ης, ἡ", ""),
            "λύω": ("lösen, auflösen", "λύω, λύσω, ἔλυσα, λέλυκα, λέλυμαι, ἐλύθην", ""),
        })
        
        # ============ MY ============
        self.vocab_dict.update({
            "μάθημα": ("Lerngegenstand, Kenntnis", "μάθημα, ατος, τό", ""),
            "μαθητής": ("Schüler", "μαθητής, οῦ, ὁ", ""),
            "μαίνομαι": ("rasen, wüten", "μαίνομαι", ""),
            "μακάριος": ("glückselig, selig", "μακάριος, α, ον", ""),
            "μακρός": ("lang, groß", "μακρός, ά, όν", ""),
            "μάλα": ("sehr", "μάλα, μᾶλλον, μάλιστα", ""),
            "μάλιστα": ("am meisten, besonders", "μάλιστα", ""),
            "μᾶλλον": ("mehr, lieber", "μᾶλλον", "μᾶλλον δέ - vielmehr"),
            "μανθάνω": ("lernen; verstehen", "μανθάνω, μαθήσομαι, ἔμαθον, μεμάθηκα", ""),
            "μάντις": ("Seher, Wahrsager", "μάντις, εως, ὁ", ""),
            "μαρτυρέω": ("bezeugen", "μαρτυρέω", ""),
            "μάρτυς": ("Zeuge", "μάρτυς, υρος, ὁ/ἡ", ""),
            "μάχη": ("Kampf", "μάχη, ης, ἡ", ""),
            "μάχομαι": ("kämpfen", "μάχομαι, μαχοῦμαι, ἐμαχεσάμην, μεμάχημαι", ""),
            "μέγας": ("groß, bedeutend", "μέγας, μεγάλη, μέγα", ""),
            "μέγεθος": ("Größe", "μέγεθος, ους, τό", ""),
            "μείς": ("Monat", "μείς, μηνός, ὁ", ""),
            "μέλει": ("es liegt am Herzen", "μέλει", "μέλει μοί τινος - ich kümmere mich um etw."),
            "μέλλω": ("im Begriff sein; sollen; zögern", "μέλλω, μελλήσω, ἐμέλλησα", "τὰ μέλλοντα - die Zukunft"),
            "μέλος": ("Glied; Lied", "μέλος, ους, τό", ""),
            "μέν": ("zwar", "μέν", "μέν...δέ - zwar...aber"),
            "μέντοι": ("freilich, allerdings", "μέντοι", ""),
            "μένω": ("bleiben, warten", "μένω, μενῶ, ἔμεινα, μεμένηκα", ""),
            "μέρος": ("Teil", "μέρος, ους, τό", "τὸ ἐμὸν μέρος - was mich betrifft"),
            "μέσος": ("mittlerer, mitten", "μέσος, η, ον", ""),
            "μετά": ("mit (+Gen.); nach (+Akk.)", "μετά", ""),
            "μετέχω": ("Anteil haben", "μετέχω", ""),
            "μέτρον": ("Maß", "μέτρον, ου, τό", ""),
            "μή": ("nicht", "μή", ""),
            "μηδέ": ("und nicht, auch nicht", "μηδέ", ""),
            "μηδείς": ("niemand, nichts", "μηδείς, μηδεμία, μηδέν", ""),
            "μήν": ("wahrlich", "μήν", ""),
            "μήτηρ": ("Mutter", "μήτηρ, τρός, ἡ", ""),
            "μηχανή": ("Kunstgriff, Mittel, Maschine", "μηχανή, ῆς, ἡ", ""),
            "μικρός": ("klein", "μικρός, ά, όν", "μικροῦ δεῖν - beinahe"),
            "μιμέομαι": ("nachahmen", "μιμέομαι", ""),
            "μιμνήσκω": ("erinnern", "μιμνήσκω", ""),
            "μισέω": ("hassen", "μισέω", ""),
            "μνήμη": ("Gedächtnis, Andenken", "μνήμη, ης, ἡ", ""),
            "μοῖρα": ("Anteil; Schicksal", "μοῖρα, ας, ἡ", ""),
            "μόνος": ("allein, einzig", "μόνος, η, ον", "μόνον - nur"),
            "μῦθος": ("Wort; Erzählung", "μῦθος, ου, ὁ", ""),
            "μύριοι": ("zehntausend", "μύριοι, αι, α", ""),
        })
        
        # ============ NY ============
        self.vocab_dict.update({
            "ναί": ("ja", "ναί", ""),
            "ναός": ("Tempel", "ναός, οῦ, ὁ", ""),
            "ναῦς": ("Schiff", "ναῦς, νεώς, ἡ", ""),
            "νεκρός": ("tot; Leichnam", "νεκρός, ά, όν", ""),
            "νέμω": ("zuteilen; weiden", "νέμω", ""),
            "νέος": ("neu, jung", "νέος, α, ον", "οἱ νέοι - die jungen Männer"),
            "νῆσος": ("Insel", "νῆσος, ου, ἡ", ""),
            "νικάω": ("siegen, besiegen", "νικάω, νικήσω, ἐνίκησα, νενίκηκα", ""),
            "νίκη": ("Sieg", "νίκη, ης, ἡ", ""),
            "νοέω": ("denken; erkennen", "νοέω", ""),
            "νομίζω": ("glauben, meinen; anerkennen", "νομίζω, νομιῶ, ἐνόμισα, νενόμικα", ""),
            "νόμιμος": ("gesetzlich", "νόμιμος, η, ον", ""),
            "νόμος": ("Gesetz; Sitte", "νόμος, ου, ὁ", ""),
            "νόσος": ("Krankheit", "νόσος, ου, ἡ", ""),
            "νοῦς": ("Verstand, Geist", "νοῦς, νοῦ, ὁ", "τὸν νοῦν προσέχειν - achten auf"),
            "νῦν": ("nun", "νῦν", ""),
            "νύξ": ("Nacht", "νύξ, νυκτός, ἡ", "νυκτός - nachts"),
        })
        
        # ============ XI ============
        self.vocab_dict.update({
            "ξένος": ("Fremder; Gast; Söldner", "ξένος, ου, ὁ", ""),
            "ξύλον": ("Holz", "ξύλον, ου, τό", ""),
        })
        
        # ============ OMICRON ============
        self.vocab_dict.update({
            "ὁ": ("der", "ὁ, ἡ, τό", "ὁ μέν...ὁ δέ - der eine...der andere"),
            "ὅδε": ("dieser hier", "ὅδε, ἥδε, τόδε", ""),
            "ὁδός": ("Weg, Reise", "ὁδός, οῦ, ἡ", ""),
            "οἶδα": ("wissen, kennen", "οἶδα, εἴσομαι", ""),
            "οἰκεῖος": ("häuslich; eigen; verwandt", "οἰκεῖος, α, ον", ""),
            "οἰκέω": ("wohnen, bewohnen", "οἰκέω, οἰκήσω, ᾤκησα", ""),
            "οἰκία": ("Haus, Gebäude", "οἰκία, ας, ἡ", ""),
            "οἶκος": ("Haus; Familie", "οἶκος, ου, ὁ", ""),
            "οἶνος": ("Wein", "οἶνος, ου, ὁ", ""),
            "οἴομαι": ("glauben, meinen", "οἴομαι/οἶμαι", ""),
            "οἷος": ("wie beschaffen", "οἷος, οία, οἷον", "οἷός τέ εἰμι - imstande sein"),
            "οἴχομαι": ("fortgehen, fortsein", "οἴχομαι", ""),
            "ὀλίγος": ("wenig, gering", "ὀλίγος, η, ον", "ὀλίγου δεῖν - beinahe"),
            "ὅλος": ("ganz", "ὅλος, η, ον", "καθ' ὅλου - im allgemeinen"),
            "ὅμοιος": ("gleich, ähnlich", "ὅμοιος, α, ον", ""),
            "ὁμολογέω": ("übereinstimmen, zustimmen", "ὁμολογέω", ""),
            "ὅμως": ("dennoch", "ὅμως", ""),
            "ὄνομα": ("Name; Ruf", "ὄνομα, ατος, τό", ""),
            "ὀνομάζω": ("nennen, benennen", "ὀνομάζω", ""),
            "ὁπλίτης": ("Schwerbewaffneter", "ὁπλίτης, ου, ὁ", ""),
            "ὅπλον": ("Waffe", "ὅπλον, ου, τό", ""),
            "ὁπότε": ("als, wenn", "ὁπότε", ""),
            "ὅπου": ("wo", "ὅπου", ""),
            "ὁράω": ("sehen", "ὁράω, ὄψομαι, εἶδον, ἑώρακα, ὦμμαι, ὤφθην", ""),
            "ὄργανον": ("Werkzeug, Instrument", "ὄργανον, ου, τό", ""),
            "ὀργή": ("Zorn", "ὀργή, ῆς, ἡ", ""),
            "ὀρθός": ("gerade, aufrecht; richtig", "ὀρθός, ή, όν", ""),
            "ὁρίζω": ("begrenzen, definieren", "ὁρίζω", ""),
            "ὁρμάω": ("sich in Bewegung setzen", "ὁρμάω", ""),
            "ὄρνις": ("Vogel", "ὄρνις, ιθος, ὁ/ἡ", ""),
            "ὄρος": ("Berg", "ὄρος, ους, τό", ""),
            "ὅς": ("welcher, der", "ὅς, ἥ, ὅ", "ὃς ἄν - wer auch immer"),
            "ὅσιος": ("heilig, recht; fromm", "ὅσιος, α, ον", ""),
            "ὅσος": ("wie groß, wie viel", "ὅσος, η, ον", "ὅσῳ...τοσούτῳ - je...desto"),
            "ὅστις": ("wer auch immer", "ὅστις, ἥτις, ὅ τι", ""),
            "ὅταν": ("immer wenn", "ὅταν", ""),
            "ὅτε": ("als, wenn", "ὅτε", ""),
            "ὅτι": ("dass, weil", "ὅτι", ""),
            "οὐ": ("nicht", "οὐ, οὐκ, οὐχ", ""),
            "οὐδέ": ("und nicht, auch nicht", "οὐδέ", ""),
            "οὐδείς": ("niemand, nichts", "οὐδείς, οὐδεμία, οὐδέν", ""),
            "οὐκέτι": ("nicht mehr", "οὐκέτι", ""),
            "οὖν": ("nun; also", "οὖν", ""),
            "οὔπω": ("noch nicht", "οὔπω", ""),
            "οὐρανός": ("Himmel", "οὐρανός, οῦ, ὁ", ""),
            "οὔτε...οὔτε": ("weder... noch", "οὔτε...οὔτε", ""),
            "οὗτος": ("dieser", "οὗτος, αὕτη, τοῦτο", ""),
            "οὕτως": ("so", "οὕτως/οὕτω", ""),
            "ὀφείλω": ("schulden, sollen", "ὀφείλω", "ὤφελες - du hättest sollen"),
            "ὀφθαλμός": ("Auge", "ὀφθαλμός, οῦ, ὁ", ""),
            "ὄψις": ("Sehkraft, Aussehen", "ὄψις, εως, ἡ", ""),
        })
        
        # ============ PI ============
        self.vocab_dict.update({
            "πάθος": ("Erlebnis; Leid, Leiden; Leidenschaft", "πάθος, ους, τό", ""),
            "παιδεία": ("Erziehung, Bildung", "παιδεία, ας, ἡ", ""),
            "παιδεύω": ("erziehen, bilden", "παιδεύω", ""),
            "παιδίον": ("Kind", "παιδίον, ου, τό", ""),
            "παῖς": ("Kind; Sklave", "παῖς, παιδός, ὁ/ἡ", ""),
            "παλαιός": ("alt", "παλαιός, ά, όν", ""),
            "πάλιν": ("wieder, zurück", "πάλιν", ""),
            "παντάπασι": ("ganz und gar", "παντάπασι", ""),
            "πάνυ": ("ganz, sehr", "πάνυ", ""),
            "παρά": ("von (+Gen.); bei (+Dat.); zu (+Akk.)", "παρά", ""),
            "παραγίγνομαι": ("hinzukommen", "παραγίγνομαι", ""),
            "παραδίδωμι": ("übergeben, überliefern", "παραδίδωμι", ""),
            "παρακαλέω": ("herbeirufen, auffordern", "παρακαλέω", ""),
            "παρασκευάζω": ("vorbereiten", "παρασκευάζω", ""),
            "πάρειμι": ("da sein, anwesend sein", "πάρειμι", "πάρεστί μοι - es steht in meiner Macht"),
            "παρέχω": ("gewähren, geben", "παρέχω", ""),
            "πᾶς": ("all, ganz, jeder", "πᾶς, πᾶσα, πᾶν", ""),
            "πάσχω": ("erleiden; erleben", "πάσχω, πείσομαι, ἔπαθον, πέπονθα", ""),
            "πατήρ": ("Vater", "πατήρ, πατρός, ὁ", ""),
            "πατρίς": ("Vaterland, Heimat", "πατρίς, ίδος, ἡ", ""),
            "παύω": ("beenden, aufhören lassen", "παύω, παύσω, ἔπαυσα", ""),
            "πείθω": ("überreden, überzeugen", "πείθω, πείσω, ἔπεισα, πέποιθα, πέπεισμαι, ἐπείσθην", ""),
            "πειράω": ("versuchen", "πειράω", ""),
            "πέμπω": ("schicken, senden", "πέμπω, πέμψω, ἔπεμψα", ""),
            "πέντε": ("fünf", "πέντε", ""),
            "περί": ("über (+Gen.); um (+Akk.)", "περί", ""),
            "πέτρα": ("Fels, Stein", "πέτρα, ας, ἡ", ""),
            "πίνω": ("trinken", "πίνω, πίομαι, ἔπιον", ""),
            "πίπτω": ("fallen", "πίπτω, πεσοῦμαι, ἔπεσον, πέπτωκα", ""),
            "πιστεύω": ("glauben, vertrauen", "πιστεύω, πιστεύσω, ἐπίστευσα", ""),
            "πίστις": ("Treue, Vertrauen", "πίστις, εως, ἡ", ""),
            "πιστός": ("treu, zuverlässig", "πιστός, ή, όν", ""),
            "πλανάομαι": ("sich verirren, umherirren", "πλανάομαι", ""),
            "πλέω": ("segeln, fahren", "πλέω, πλεύσομαι, ἔπλευσα", ""),
            "πλήθος": ("Menge", "πλήθος, ους, τό", ""),
            "πλήν": ("außer", "πλήν", ""),
            "πλήττω": ("schlagen", "πλήττω", ""),
            "πλοῖον": ("Schiff", "πλοῖον, ου, τό", ""),
            "πλοῦτος": ("Reichtum", "πλοῦτος, ου, ὁ", ""),
            "ποιέω": ("machen, tun; dichten", "ποιέω, ποιήσω, ἐποίησα, πεποίηκα, πεποίημαι, ἐποιήθην", ""),
            "ποίησις": ("Dichtung, Poesie", "ποίησις, εως, ἡ", ""),
            "ποιητής": ("Dichter; Schöpfer", "ποιητής, οῦ, ὁ", ""),
            "ποῖος": ("wie beschaffen?", "ποῖος, α, ον", ""),
            "πόλεμος": ("Krieg", "πόλεμος, ου, ὁ", ""),
            "πόλις": ("Stadt; Staat", "πόλις, εως, ἡ", ""),
            "πολιτεία": ("Staatsverfassung", "πολιτεία, ας, ἡ", ""),
            "πολίτης": ("Bürger", "πολίτης, ου, ὁ", ""),
            "πολιτικός": ("bürgerlich, politisch", "πολιτικός, ή, όν", ""),
            "πολλάκις": ("oft", "πολλάκις", ""),
            "πολύς": ("viel", "πολύς, πολλή, πολύ", "οἱ πολλοί - die meisten"),
            "πονηρός": ("schlecht, böse", "πονηρός, ά, όν", ""),
            "πόνος": ("Mühe, Arbeit", "πόνος, ου, ὁ", ""),
            "πορεύομαι": ("reisen, marschieren", "πορεύομαι, πορεύσομαι, ἐπορεύθην", ""),
            "ποταμός": ("Fluss", "ποταμός, οῦ, ὁ", ""),
            "πότε": ("wann?", "πότε", ""),
            "ποτέ": ("einst, jemals", "ποτέ", ""),
            "πότερος": ("welcher von beiden?", "πότερος, α, ον", ""),
            "ποῦ": ("wo?", "ποῦ", ""),
            "πούς": ("Fuß", "πούς, ποδός, ὁ", ""),
            "πρᾶγμα": ("Tat, Sache, Angelegenheit", "πρᾶγμα, ατος, τό", "πράγματα παρέχω - Schwierigkeiten bereiten"),
            "πρᾶξις": ("Handlung, Tätigkeit", "πρᾶξις, εως, ἡ", ""),
            "πράττω": ("tun, handeln", "πράττω, πράξω, ἔπραξα, πέπραχα", "εὖ πράττω - es geht mir gut"),
            "πρέπει": ("es gehört sich", "πρέπει", ""),
            "πρέσβυς": ("alter Mann; Gesandter", "πρέσβυς, εως, ὁ", ""),
            "πρίν": ("ehe, bevor", "πρίν", ""),
            "πρό": ("vor", "πρό", ""),
            "πρός": ("zu, gegen, bei", "πρός", ""),
            "προσέχω": ("hinlenken", "προσέχω", "προσέχω τὸν νοῦν - achten auf"),
            "πρόσωπον": ("Gesicht; Person", "πρόσωπον, ου, τό", ""),
            "πρότερος": ("der frühere", "πρότερος, α, ον", "πρότερον - früher"),
            "πρῶτος": ("der erste", "πρῶτος, η, ον", "πρῶτον - zuerst"),
            "πυνθάνομαι": ("sich erkundigen, erfahren", "πυνθάνομαι, πεύσομαι, ἐπυθόμην, πέπυσμαι", ""),
            "πῦρ": ("Feuer", "πῦρ, πυρός, τό", ""),
            "πώποτε": ("jemals", "πώποτε", ""),
            "πῶς": ("wie?", "πῶς", ""),
            "πως": ("irgendwie", "πως", ""),
        })
        
        # ============ RHO ============
        self.vocab_dict.update({
            "ῥᾴδιος": ("leicht", "ῥᾴδιος, α, ον", ""),
            "ῥέω": ("fließen", "ῥέω", ""),
            "ῥήτωρ": ("Redner", "ῥήτωρ, ορος, ὁ", ""),
        })
        
        # ============ SIGMA ============
        self.vocab_dict.update({
            "σαφής": ("deutlich, klar", "σαφής, ές", ""),
            "σεαυτοῦ": ("deiner selbst", "σεαυτοῦ, ῆς, οῦ", ""),
            "σέβομαι": ("verehren", "σέβομαι", ""),
            "σημαίνω": ("zeigen, anzeigen", "σημαίνω", ""),
            "σῖτος": ("Getreide, Nahrung", "σῖτος, ου, ὁ", ""),
            "σκηνή": ("Zelt; Bühne", "σκηνή, ῆς, ἡ", ""),
            "σκοπέω": ("betrachten, prüfen", "σκοπέω", ""),
            "σός": ("dein", "σός, σή, σόν", ""),
            "σοφία": ("Weisheit, Klugheit", "σοφία, ας, ἡ", ""),
            "σοφός": ("weise, klug", "σοφός, ή, όν", ""),
            "σπεύδω": ("eilen, sich beeilen", "σπεύδω", ""),
            "σπουδάζω": ("sich beeilen, sich bemühen", "σπουδάζω", ""),
            "σπουδή": ("Eifer, Ernst; Eile", "σπουδή, ῆς, ἡ", ""),
            "στάσις": ("Aufstand, Unruhe", "στάσις, εως, ἡ", ""),
            "στέφανος": ("Kranz, Siegeskranz", "στέφανος, ου, ὁ", ""),
            "στοά": ("Säulenhalle", "στοά, ᾶς, ἡ", ""),
            "στρατηγός": ("Feldherr", "στρατηγός, οῦ, ὁ", ""),
            "στρατιώτης": ("Soldat", "στρατιώτης, ου, ὁ", ""),
            "στρατός": ("Heer", "στρατός, οῦ, ὁ", ""),
            "στρέφω": ("drehen, wenden", "στρέφω", ""),
            "σύ": ("du", "σύ, σοῦ", ""),
            "συγγίγνομαι": ("zusammenkommen", "συγγίγνομαι", ""),
            "συγχωρέω": ("nachgeben, zustimmen", "συγχωρέω", ""),
            "συμβαίνω": ("sich ereignen", "συμβαίνω, συμβήσομαι, συνέβην, συμβέβηκα", ""),
            "συμβουλεύω": ("raten", "συμβουλεύω", ""),
            "σύμμαχος": ("verbündet", "σύμμαχος, ον", ""),
            "σύν": ("mit", "σύν", ""),
            "σύνειμι": ("zusammen sein", "σύνειμι", ""),
            "συνίημι": ("verstehen", "συνίημι", ""),
            "σφόδρα": ("sehr", "σφόδρα", ""),
            "σχεδόν": ("beinahe", "σχεδόν", ""),
            "σχῆμα": ("Haltung, Gestalt", "σχῆμα, ατος, τό", ""),
            "σχολή": ("Muße; Schule", "σχολή, ῆς, ἡ", ""),
            "σῴζω": ("retten, bewahren", "σῴζω, σώσω, ἔσωσα, σέσωκα", ""),
            "σῶμα": ("Körper", "σῶμα, ατος, τό", ""),
            "σωτήρ": ("Retter", "σωτήρ, ῆρος, ὁ", ""),
            "σωφροσύνη": ("Besonnenheit", "σωφροσύνη, ης, ἡ", ""),
            "σώφρων": ("besonnen, vernünftig", "σώφρων, ον", ""),
        })
        
        # ============ TAU ============
        self.vocab_dict.update({
            "τάττω": ("aufstellen, anordnen", "τάττω, τάξω, ἔταξα, τέταχα, τέταγμαι, ἐτάχθην", ""),
            "ταχύς": ("schnell", "ταχύς, εῖα, ύ", ""),
            "τε": ("und", "τε", "...τε...καί - sowohl...als auch"),
            "τεῖχος": ("Mauer", "τεῖχος, ους, τό", ""),
            "τεκμήριον": ("Beweis", "τεκμήριον, ου, τό", ""),
            "τέκνον": ("Kind", "τέκνον, ου, τό", ""),
            "τελευτάω": ("beenden; sterben", "τελευτάω", ""),
            "τελέω": ("vollenden, bezahlen", "τελέω", ""),
            "τέλος": ("Ende; Ziel", "τέλος, ους, τό", "τέλος - endlich"),
            "τέμνω": ("schneiden", "τέμνω, τεμῶ, ἔτεμον", ""),
            "τέτταρες": ("vier", "τέτταρες, α", ""),
            "τέχνη": ("Kunst, Fähigkeit", "τέχνη, ης, ἡ", ""),
            "τίθημι": ("setzen, stellen, legen", "τίθημι, θήσω, ἔθηκα, τέθηκα, κεῖμαι, ἐτέθην", ""),
            "τίκτω": ("zeugen, gebären", "τίκτω, τέξομαι, ἔτεκον, τέτοκα", ""),
            "τιμάω": ("ehren", "τιμάω, τιμήσω, ἐτίμησα, τετίμηκα", ""),
            "τιμή": ("Ehre", "τιμή, ῆς, ἡ", ""),
            "τις": ("jemand, irgendeiner", "τις, τι", ""),
            "τίς": ("wer? was?", "τίς, τί", ""),
            "τοι": ("wahrlich", "τοι", ""),
            "τοίνυν": ("also, folglich", "τοίνυν", ""),
            "τοιοῦτος": ("solcher, derartig", "τοιοῦτος, αύτη, οῦτο", ""),
            "τολμάω": ("wagen", "τολμάω", ""),
            "τόπος": ("Ort, Platz", "τόπος, ου, ὁ", ""),
            "τοσοῦτος": ("so groß", "τοσοῦτος, αύτη, οῦτο", ""),
            "τότε": ("da, damals, dann", "τότε", ""),
            "τρεῖς": ("drei", "τρεῖς, τρία", ""),
            "τρέπω": ("wenden", "τρέπω, τρέψω, ἔτρεψα", ""),
            "τρέφω": ("ernähren, aufziehen", "τρέφω, θρέψω, ἔθρεψα, τέθραμμαι, ἐτράφην", ""),
            "τρόπος": ("Art und Weise; Charakter", "τρόπος, ου, ὁ", ""),
            "τυγχάνω": ("treffen; gerade tun", "τυγχάνω, τεύξομαι, ἔτυχον, τετύχηκα", "τυγχάνω ποιῶν τι - gerade etw. tun"),
            "τύπτω": ("schlagen", "τύπτω", ""),
            "τύραννος": ("Gewaltherrscher", "τύραννος, ου, ὁ", ""),
            "τύχη": ("Zufall, Schicksal, Glück", "τύχη, ης, ἡ", ""),
        })
        
        # ============ YPSILON ============
        self.vocab_dict.update({
            "ὕβρις": ("Hochmut; Freveltat", "ὕβρις, εως, ἡ", ""),
            "ὑγίεια": ("Gesundheit", "ὑγίεια, ας, ἡ", ""),
            "ὑγιής": ("gesund", "ὑγιής, ές", ""),
            "ὕδωρ": ("Wasser", "ὕδωρ, ατος, τό", ""),
            "υἱός": ("Sohn", "υἱός, οῦ, ὁ", ""),
            "ὑμεῖς": ("ihr", "ὑμεῖς, ὑμῶν, ὑμῖν, ὑμᾶς", ""),
            "ὑμέτερος": ("euer", "ὑμέτερος, α, ον", ""),
            "ὕπνος": ("Schlaf", "ὕπνος, ου, ὁ", ""),
            "ὑπό": ("unter (+Gen./Dat./Akk.)", "ὑπό", ""),
            "ὑπολαμβάνω": ("vermuten; entgegnen", "ὑπολαμβάνω", ""),
        })
        
        # ============ PHI ============
        self.vocab_dict.update({
            "φαίνω": ("zeigen; erscheinen", "φαίνω, φανῶ, ἔφηνα, πέφηνα, πέφασμαι, ἐφάνην", ""),
            "φανερός": ("sichtbar, deutlich", "φανερός, ά, όν", ""),
            "φάρμακον": ("Heilmittel, Gift", "φάρμακον, ου, τό", ""),
            "φάσκω": ("sagen, behaupten", "φάσκω", ""),
            "φαῦλος": ("schlecht", "φαῦλος, η, ον", ""),
            "φέρω": ("tragen, bringen, ertragen", "φέρω, οἴσω, ἤνεγκον, ἐνήνοχα, ἐνήνεγμαι, ἠνέχθην", ""),
            "φεύγω": ("fliehen, meiden", "φεύγω, φεύξομαι, ἔφυγον, πέφευγα", ""),
            "φημί": ("sagen, behaupten", "φημί, φήσω, ἔφησα/ἔφην", ""),
            "φθονέω": ("beneiden", "φθονέω", ""),
            "φιλέω": ("lieben", "φιλέω", ""),
            "φιλία": ("Freundschaft", "φιλία, ας, ἡ", ""),
            "φίλος": ("lieb; Freund", "φίλος, η, ον", ""),
            "φιλοσοφία": ("Philosophie", "φιλοσοφία, ας, ἡ", ""),
            "φιλόσοφος": ("Philosoph", "φιλόσοφος, ου, ὁ", ""),
            "φοβέομαι": ("sich fürchten", "φοβέομαι, φοβήσομαι, ἐφοβήθην", ""),
            "φόβος": ("Furcht", "φόβος, ου, ὁ", ""),
            "φονεύω": ("ermorden", "φονεύω", ""),
            "φράζω": ("sagen, zeigen", "φράζω, φράσω, ἔφρασα", ""),
            "φρονέω": ("denken, Verstand haben", "φρονέω", ""),
            "φρόνιμος": ("verständig, klug", "φρόνιμος, ον", ""),
            "φροντίζω": ("sich kümmern", "φροντίζω", ""),
            "φυλάττω": ("bewachen, bewahren", "φυλάττω, φυλάξω, ἐφύλαξα", ""),
            "φύσις": ("Natur; Wesen", "φύσις, εως, ἡ", ""),
            "φωνή": ("Stimme; Klang", "φωνή, ῆς, ἡ", ""),
            "φῶς": ("Licht", "φῶς, φωτός, τό", ""),
        })
        
        # ============ CHI ============
        self.vocab_dict.update({
            "χαίρω": ("sich freuen", "χαίρω, χαιρήσω, κεχάρηκα, ἐχάρην", "χαῖρε - sei gegrüßt!"),
            "χαλεπός": ("schwer, schwierig", "χαλεπός, ή, όν", ""),
            "χάρις": ("Gefälligkeit, Dank; Anmut", "χάρις, ιτος, ἡ", "χάριν ἀποδίδωμι - danken"),
            "χείρ": ("Hand", "χείρ, χειρός, ἡ", ""),
            "χείρων": ("schlechter", "χείρων, χεῖρον", "Komp. zu κακός"),
            "χέω": ("gießen, vergießen", "χέω", ""),
            "χορός": ("Tanz, Reigen", "χορός, οῦ, ὁ", ""),
            "χράομαι": ("gebrauchen, benutzen", "χράομαι, χρήσομαι, ἐχρησάμην, κέχρημαι", ""),
            "χρή": ("es ist nötig, man muss", "χρή", ""),
            "χρῆμα": ("Sache; pl. Geld", "χρῆμα, ατος, τό", ""),
            "χρήσιμος": ("nützlich, brauchbar", "χρήσιμος, η, ον", ""),
            "χρόνος": ("Zeit", "χρόνος, ου, ὁ", ""),
            "χρυσός": ("Gold", "χρυσός, οῦ, ὁ", ""),
            "χώρα": ("Land, Gegend; Ort", "χώρα, ας, ἡ", ""),
            "χωρέω": ("weichen, gehen", "χωρέω", ""),
            "χωρίς": ("getrennt von, ohne", "χωρίς", ""),
        })
        
        # ============ PSI ============
        self.vocab_dict.update({
            "ψεύδω": ("täuschen; lügen", "ψεύδω, ψεύσω, ἔψευσα", ""),
            "ψυχή": ("Seele, Leben", "ψυχή, ῆς, ἡ", ""),
            "ψυχρός": ("kalt", "ψυχρός, ά, όν", ""),
        })
        
        # ============ OMEGA ============
        self.vocab_dict.update({
            "ὦ": ("o!", "ὦ", ""),
            "ὦδε": ("so, folgendermaßen", "ὦδε", ""),
            "ᾠδή": ("Gesang, Lied", "ᾠδή, ῆς, ἡ", ""),
            "ὥρα": ("Jahreszeit; rechte Zeit", "ὥρα, ας, ἡ", ""),
            "ὡς": ("wie, dass; damit", "ὡς", ""),
            "ὥσπερ": ("wie, gerade wie", "ὥσπερ", ""),
            "ὥστε": ("so dass; daher", "ὥστε", ""),
            "ὠφελέω": ("nützen; unterstützen", "ὠφελέω", ""),
            "ὠφέλιμος": ("nützlich", "ὠφέλιμος, ον", ""),
        })
    
    def finde_bedeutung(self, griechisch: str) -> Tuple[Optional[List[str]], bool, str]:
        """
        Sucht die Bedeutung eines griechischen Wortes im Omega-Wortschatz.
        Gibt zurück: (Liste der Bedeutungen, gefunden, Stammformen/Zusatzinfo)
        """
        suchbegriff = griechisch.strip()
        
        # Direkte Suche
        if suchbegriff in self.vocab_dict:
            bedeutung, stammformen, zusatz = self.vocab_dict[suchbegriff]
            # Alle Bedeutungen einzeln auflisten (durch ; getrennt)
            bedeutungen = [b.strip() for b in bedeutung.split(';')]
            return bedeutungen, True, f"{stammformen} {zusatz}".strip()
        
        # Suche mit Synonymen
        if suchbegriff in self.synonyme:
            hauptform = self.synonyme[suchbegriff]
            if hauptform in self.vocab_dict:
                bedeutung, stammformen, zusatz = self.vocab_dict[hauptform]
                bedeutungen = [b.strip() for b in bedeutung.split(';')]
                return bedeutungen, True, f"{stammformen} {zusatz} [Synonym zu {hauptform}]".strip()
        
        # Unscharfe Suche (ohne Akzente)
        suchbegriff_no_accent = self._remove_accents(suchbegriff)
        for key in self.vocab_dict:
            if self._remove_accents(key) == suchbegriff_no_accent:
                bedeutung, stammformen, zusatz = self.vocab_dict[key]
                bedeutungen = [b.strip() for b in bedeutung.split(';')]
                return bedeutungen, True, f"{stammformen} {zusatz}".strip()
        
        return None, False, ""
    
    def _remove_accents(self, text: str) -> str:
        """Entfernt Akzente für unscharfe Suche"""
        accent_map = {
            'ά': 'α', 'ὰ': 'α', 'ἀ': 'α', 'ἁ': 'α', 'ἂ': 'α', 'ἃ': 'α', 'ἄ': 'α', 'ἅ': 'α',
            'έ': 'ε', 'ὲ': 'ε', 'ἐ': 'ε', 'ἑ': 'ε', 'ἒ': 'ε', 'ἓ': 'ε', 'ἔ': 'ε', 'ἕ': 'ε',
            'ή': 'η', 'ὴ': 'η', 'ἠ': 'η', 'ἡ': 'η', 'ἢ': 'η', 'ἣ': 'η', 'ἤ': 'η', 'ἥ': 'η',
            'ί': 'ι', 'ὶ': 'ι', 'ἰ': 'ι', 'ἱ': 'ι', 'ἲ': 'ι', 'ἳ': 'ι', 'ἴ': 'ι', 'ἵ': 'ι',
            'ό': 'ο', 'ὸ': 'ο', 'ὀ': 'ο', 'ὁ': 'ο', 'ὂ': 'ο', 'ὃ': 'ο', 'ὄ': 'ο', 'ὅ': 'ο',
            'ύ': 'υ', 'ὺ': 'υ', 'ὐ': 'υ', 'ὑ': 'υ', 'ὒ': 'υ', 'ὓ': 'υ', 'ὔ': 'υ', 'ὕ': 'υ',
            'ώ': 'ω', 'ὼ': 'ω', 'ὠ': 'ω', 'ὡ': 'ω', 'ὢ': 'ω', 'ὣ': 'ω', 'ὤ': 'ω', 'ὥ': 'ω',
            'ΐ': 'ι', 'ῒ': 'ι', 'ῗ': 'ι', 'ΰ': 'υ', 'ῢ': 'υ', 'ῧ': 'υ',
            'ᾶ': 'α', 'ῆ': 'η', 'ῖ': 'ι', 'ῦ': 'υ', 'ῶ': 'ω',
        }
        result = []
        for char in text:
            result.append(accent_map.get(char, char))
        return ''.join(result)


# ============================================
# PDF-PARSER
# ============================================

class VokabelPDFParser:
    """Extrahiert Vokabeln aus hochgeladenen PDFs"""
    
    def __init__(self):
        self.omega = OmegaWortschatz()
    
    def parse_pdf(self, pdf_file) -> List[VokabelEintrag]:
        """Parst eine Vokabellisten-PDF und extrahiert die Einträge"""
        eintraege = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    eintraege.extend(self._parse_text(text))
        
        # Nach Position sortieren
        eintraege.sort(key=lambda x: x.position)
        return eintraege
    
    def _parse_text(self, text: str) -> List[VokabelEintrag]:
        """Extrahiert Vokabeleinträge aus Text"""
        eintraege = []
        lines = text.split('\n')
        
        current_pos = 1
        
        # Griechische Buchstaben (mit Akzenten und Spiritus)
        greek_pattern = r'([α-ωἀ-ὥἐ-ἕἠ-ὥἰ-ΐἱ-ἵὀ-ὅὐ-ϋὑ-ὕὠ-ὧᾀ-ᾠᾰ-ᾱᾳ-ῳ]+)'
        
        for line in lines:
            # Suche nach griechischen Wörtern
            matches = re.findall(greek_pattern, line)
            
            for match in matches:
                # Ignoriere zu kurze Wörter
                if len(match) >= 2:
                    # Prüfe ob es eine Nummer ist
                    if not match.isdigit():
                        eintrag = VokabelEintrag(
                            position=current_pos,
                            griechisch=match,
                            original_zeile=line
                        )
                        
                        # Suche Bedeutung
                        bedeutungen, gefunden, zusatz = self.omega.finde_bedeutung(match)
                        eintrag.bedeutungen = bedeutungen if bedeutungen else []
                        eintrag.gefunden = gefunden
                        eintrag.stammformen = zusatz
                        
                        eintraege.append(eintrag)
                        current_pos += 1
        
        return eintraege


# ============================================
# PDF-GENERATOR
# ============================================

class PDFGenerator:
    """Erstellt PDFs mit den Vokabeln und Bedeutungen"""
    
    @staticmethod
    def erstelle_pdf(eintraege: List[VokabelEintrag]) -> BytesIO:
        """Erstellt eine PDF-Tabelle mit allen Vokabeln und Bedeutungen"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Stile
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Titel
        titel = Paragraph(f"Vokabelliste mit Bedeutungen", title_style)
        story.append(titel)
        story.append(Spacer(1, 0.5*cm))
        
        # Tabellenkopf
        data = [['Nr.', 'Griechisch', 'Stammformen', 'Bedeutungen']]
        
        # Datenzeilen
        for eintrag in eintraege:
            nr = str(eintrag.position)
            griechisch = eintrag.griechisch
            
            # Stammformen
            if eintrag.gefunden and eintrag.stammformen:
                stammformen = eintrag.stammformen
            else:
                stammformen = "nicht gefunden"
            
            # Bedeutungen
            if eintrag.gefunden and eintrag.bedeutungen:
                bedeutungen = "; ".join(eintrag.bedeutungen)
            else:
                bedeutungen = "⚠️ NICHT GEFUNDEN"
                if not eintrag.gefunden:
                    bedeutungen += " - Bitte manuell ergänzen"
            
            data.append([nr, griechisch, stammformen, bedeutungen])
        
        # Tabelle erstellen
        table = Table(data, colWidths=[1.5*cm, 4*cm, 6*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        
        # Fußnote mit Lizenz
        story.append(Spacer(1, 1*cm))
        fussnote = Paragraph(
            "Vokabeldaten basierend auf dem Omega-Wortschatz von Ulrich Gebhardt, Freiburg - CC BY-NC-SA 4.0",
            styles['Italic']
        )
        story.append(fussnote)
        
        doc.build(story)
        buffer.seek(0)
        return buffer


# ============================================
# STREAMLIT UI
# ============================================

def main():
    """Hauptfunktion der Streamlit-App"""
    
    # Seitenkonfiguration
    st.set_page_config(
        page_title="Altgriechisch Vokabeltrainer",
        page_icon="📚",
        layout="wide"
    )
    
    # Titel
    st.title("📚 Altgriechisch Vokabeltrainer")
    st.markdown("---")
    
    # Sidebar mit Info
    with st.sidebar:
        st.header("ℹ️ Info")
        st.markdown("""
        Diese App extrahiert griechische Vokabeln aus PDF-Dateien 
        und fügt die deutschen Bedeutungen aus dem Omega-Wortschatz hinzu.
        
        **Omega-Wortschatz:**
        - Über 800 griechische Wörter
        - CC BY-NC-SA 4.0 Lizenz
        - Autor: Ulrich Gebhardt, Freiburg
        
        **Funktionen:**
        - PDF-Upload
        - Automatische Worterkennung
        - Bedeutungssuche
        - PDF-Export
        - Manuelle Korrektur
        """)
        
        st.markdown("---")
        st.caption("Erstellt für Altgriechisch-Unterricht")
    
    # Hauptbereich
    uploaded_file = st.file_uploader(
        "📤 Wählen Sie eine Vokabellisten-PDF aus",
        type=['pdf'],
        help="Laden Sie Ihre Vokabelliste im PDF-Format hoch"
    )
    
    if uploaded_file is not None:
        with st.spinner("📖 Analysiere PDF und suche Bedeutungen..."):
            parser = VokabelPDFParser()
            eintraege = parser.parse_pdf(uploaded_file)
        
        if eintraege:
            st.success(f"✅ {len(eintraege)} Vokabeln gefunden!")
            
            # Statistik
            gefunden = sum(1 for e in eintraege if e.gefunden)
            nicht_gefunden = len(eintraege) - gefunden
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt", len(eintraege))
            with col2:
                st.metric("Gefunden", gefunden, delta=f"{gefunden/len(eintraege)*100:.0f}%")
            with col3:
                st.metric("Nicht gefunden", nicht_gefunden)
            
            st.markdown("---")
            
            # Manuelle Korrektur
            st.subheader("✏️ Manuelle Korrektur")
            st.caption("Hier können Sie fehlende oder falsche Bedeutungen korrigieren")
            
            korrigierte_eintraege = []
            
            for i, eintrag in enumerate(eintraege):
                with st.expander(f"{eintrag.position}. {eintrag.griechisch}", expanded=False):
                    col_a, col_b = st.columns([1, 3])
                    
                    with col_a:
                        st.markdown(f"**Gefunden:** {'✅' if eintrag.gefunden else '❌'}")
                        if eintrag.stammformen:
                            st.markdown(f"**Stammformen:** {eintrag.stammformen}")
                    
                    with col_b:
                        if eintrag.gefunden and eintrag.bedeutungen:
                            aktuelle_bedeutung = "; ".join(eintrag.bedeutungen)
                        else:
                            aktuelle_bedeutung = ""
                        
                        neue_bedeutung = st.text_area(
                            f"Bedeutung für {eintrag.griechisch}",
                            value=aktuelle_bedeutung,
                            key=f"korrektur_{i}",
                            height=100
                        )
                        
                        if neue_bedeutung and neue_bedeutung != aktuelle_bedeutung:
                            eintrag.bedeutungen = [b.strip() for b in neue_bedeutung.split(';')]
                            eintrag.gefunden = True
                            st.success("✅ Korrigiert!")
                    
                    korrigierte_eintraege.append(eintrag)
            
            st.markdown("---")
            
            # PDF Export
            st.subheader("📥 PDF Export")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 PDF mit Bedeutungen erstellen", type="primary"):
                    with st.spinner("📄 Erstelle PDF..."):
                        pdf_buffer = PDFGenerator.erstelle_pdf(korrigierte_eintraege)
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"vokabeln_mit_bedeutungen_{timestamp}.pdf"
                        
                        st.download_button(
                            label="⬇️ PDF herunterladen",
                            data=pdf_buffer,
                            file_name=filename,
                            mime="application/pdf"
                        )
            
            with col2:
                # CSV Export als Alternative
                if st.button("📊 Als CSV exportieren"):
                    data = []
                    for e in korrigierte_eintraege:
                        data.append({
                            'Position': e.position,
                            'Griechisch': e.griechisch,
                            'Stammformen': e.stammformen if e.stammformen else "",
                            'Bedeutungen': '; '.join(e.bedeutungen) if e.bedeutungen else "",
                            'Gefunden': e.gefunden
                        })
                    
                    df = pd.DataFrame(data)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"vokabeln_mit_bedeutungen_{timestamp}.csv"
                    
                    st.download_button(
                        label="⬇️ CSV herunterladen",
                        data=csv,
                        file_name=filename,
                        mime="text/csv"
                    )
            
            # Vorschau
            st.markdown("---")
            st.subheader("👁️ Vorschau")
            
            preview_data = []
            for e in korrigierte_eintraege[:10]:  # Nur erste 10 anzeigen
                preview_data.append({
                    'Nr.': e.position,
                    'Griechisch': e.griechisch,
                    'Bedeutung': '; '.join(e.bedeutungen) if e.bedeutungen else "❌ Nicht gefunden",
                    'Status': '✅' if e.gefunden else '❌'
                })
            
            if preview_data:
                df_preview = pd.DataFrame(preview_data)
                st.dataframe(df_preview, use_container_width=True)
                
                if len(korrigierte_eintraege) > 10:
                    st.caption(f"*Zeige 10 von {len(korrigierte_eintraege)} Einträgen*")
            
        else:
            st.warning("⚠️ Keine griechischen Vokabeln in der PDF gefunden.")
            st.info("""
            **Tipps:**
            - Stellen Sie sicher, dass die PDF Text enthält (kein eingescanntes Bild)
            - Die griechischen Buchstaben müssen korrekt codiert sein
            - Versuchen Sie eine andere PDF-Datei
            """)
    
    else:
        # Platzhalter wenn keine Datei hochgeladen
        st.info("👈 Bitte laden Sie eine Vokabellisten-PDF hoch")
        
        # Beispiel
        st.markdown("---")
        st.subheader("📋 Beispiel")
        st.markdown("""
        Die App erwartet PDFs im Format Ihrer Vokabelliste:
        
        ```
        1ὁ ἀνήρ (1)τοῦ ἀνδρός
        2δός (3)ἤ, ὅ
        3μάλα (3)μάλλον μάλιστα
        ...
        ```
        
        Die App extrahiert automatisch alle griechischen Wörter 
        und sucht die deutschen Bedeutungen im Omega-Wortschatz.
        """)


if __name__ == "__main__":
    main()
