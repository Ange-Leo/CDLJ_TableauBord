import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(
    page_title="CDLJ - Tableau de Bord",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def charger_logo():
    """Charger le logo depuis le système de fichiers"""
    try:
        logo_paths = [
            "Logo CDLJ.jpg",
            "./Logo CDLJ.jpg",
            "logo.jpg",
            "images/Logo CDLJ.jpg"
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                with open(path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                return f'data:image/jpeg;base64,{encoded_string}'
        
        return None
        
    except Exception as e:
        st.sidebar.warning(f"⚠️ Logo non chargé: {e}")
        return None

def afficher_logo():
    """Afficher le logo dans la sidebar"""
    logo_data = charger_logo()
    if logo_data:
        st.sidebar.markdown(
            f'<div style="text-align: center;"><img src="{logo_data}" width="150" style="border-radius: 10px;"></div>',
            unsafe_allow_html=True
        )
    st.sidebar.markdown(
        '<div style="text-align: center; font-weight: bold; color: #2E86AB; margin-top: 10px;">Communauté Diocésaine des Lecteurs Juniors</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<div style="text-align: center; color: #2E86AB;">Archidiocèse de Cotonou</div>',
        unsafe_allow_html=True
    )

# Dictionnaire des vicariats (à adapter selon votre organisation)
VICARIATS = {
    "Cotonou": ["St Michel", "St Jean", "Notre Dame", "St Pierre", "St Paul"],
    "Abomey-Calavi": ["St Jacques", "Ste Marie", "St Marc"],
    "Porto-Novo": ["St Jean-Baptiste", "St Luc", "St Matthieu"],
    "Ouidah": ["St Thomas", "St Barthélémy"]
}

# Ordre des grades
GRADES_ORDRE = ['Lectorat 2', 'Animation 1', 'Animation 2', 'Formation 1', 'Formation 2']

def determiner_vicariat(paroisse):
    """Déterminer le vicariat à partir de la paroisse"""
    for vicariat, paroisses in VICARIATS.items():
        if paroisse in paroisses:
            return vicariat
    return "Non spécifié"

def detecter_vicariats_automatiquement(df_candidats):
    """Détecter automatiquement les vicariats depuis les données"""
    # Vérifier différentes variantes de noms de colonnes
    noms_vicariat_possibles = ['vicariat', 'Vicariat', 'vicariats', 'Vicariats', 'zone', 'Zone', 'secteur', 'Secteur']
    
    for nom_colonne in noms_vicariat_possibles:
        if nom_colonne in df_candidats.columns:
            vicariats_uniques = df_candidats[nom_colonne].dropna().unique()
            st.info(f"Vicariats détectés dans la colonne '{nom_colonne}': {list(vicariats_uniques)}")
            return list(vicariats_uniques), nom_colonne
    
    st.warning("Aucune colonne de vicariat trouvée dans les données")
    return ["Non spécifié"], "vicariat"

def normaliser_colonne_vicariat(df):
    """Normaliser la colonne vicariat pour avoir toujours 'vicariat' comme nom de colonne"""
    noms_vicariat_possibles = ['vicariat', 'Vicariat', 'vicariats', 'Vicariats', 'zone', 'Zone', 'secteur', 'Secteur']
    
    for nom_colonne in noms_vicariat_possibles:
        if nom_colonne in df.columns:
            if nom_colonne != 'vicariat':
                df['vicariat'] = df[nom_colonne]
                st.info(f"Colonne '{nom_colonne}' renommée en 'vicariat'")
            return df
    
    # Si aucune colonne n'est trouvée, créer une colonne vicariat par défaut
    if 'paroisse' in df.columns:
        df['vicariat'] = df['paroisse'].apply(determiner_vicariat)
        st.info("Colonne 'vicariat' créée à partir des paroisses")
    else:
        df['vicariat'] = "Non spécifié"
        st.warning("Colonne 'vicariat' créée avec valeur par défaut")
    
    return df

class TableauBordCompositions:
    def __init__(self, df_candidats, df_resultats, activite):
        self.df_candidats = df_candidats
        self.df_resultats = df_resultats
        self.activite = activite
    
    def afficher_entete_activite(self):
        """Afficher l'en-tête avec le nom de l'activité"""
        annee = datetime.now().year
        if self.activite == "weekend":
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2E86AB 0%, #1B5E7A 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; font-size: 2.5em;">🎯 Week-end de Formation Diocésaine des Animateurs</h1>
                <h2 style="margin: 10px 0 0 0; font-weight: 300;">Année {annee} - Tableau de Bord des Compositions</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #A23B72 0%, #7A2A5A 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; font-size: 2.5em;">📚 Session Diocésaine des Lecteurs Juniors</h1>
                <h2 style="margin: 10px 0 0 0; font-weight: 300;">Année {annee} - Tableau de Bord des Compositions</h2>
            </div>
            """, unsafe_allow_html=True)
    
    def afficher_kpis(self):
        """Afficher les indicateurs clés"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Candidats", len(self.df_candidats))
        
        with col2:
            if not self.df_resultats.empty and 'decision' in self.df_resultats.columns:
                # Considérer Admis et Admis_Passe au grade immédiatement supérieur comme "Admis"
                admis = self.df_resultats[
                    (self.df_resultats['decision'] == 'Admis') | 
                    (self.df_resultats['decision'] == 'Admis_Passe au grade immédiatement supérieur')
                ]
                if len(self.df_resultats) > 0:
                    taux_reussite = (len(admis) / len(self.df_resultats) * 100)
                    st.metric("Taux de Réussite", f"{taux_reussite:.1f}%")
                else:
                    st.metric("Taux de Réussite", "N/A")
            else:
                st.metric("Taux de Réussite", "N/A")
        
        with col3:
            if not self.df_resultats.empty and 'moyenne' in self.df_resultats.columns:
                meilleure_moyenne = self.df_resultats['moyenne'].max()
                st.metric("Meilleure Moyenne", f"{meilleure_moyenne:.2f}")
            else:
                st.metric("Meilleure Moyenne", "N/A")
        
        with col4:
            st.metric("Nombre de Grades", self.df_candidats['grade'].nunique())
        
        with col5:
            st.metric("Nombre de Vicariats", self.df_candidats['vicariat'].nunique())
    
    def afficher_repartition_grades(self):
        """Afficher la répartition par grade avec des tableaux"""
        st.subheader("📈 Répartition des Candidats")
        
        if not self.df_candidats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Compter les candidats par grade
                count_by_grade = self.df_candidats['grade'].value_counts().reset_index()
                count_by_grade.columns = ['Grade', 'Nombre de Candidats']
                
                # Réorganiser selon l'ordre défini
                count_by_grade['Grade'] = pd.Categorical(count_by_grade['Grade'], categories=GRADES_ORDRE, ordered=True)
                count_by_grade = count_by_grade.sort_values('Grade')
                
                st.write("**Nombre de candidats par grade:**")
                st.dataframe(count_by_grade, use_container_width=True)
                
                # Graphique avec couleurs personnalisées
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                bars = ax.bar(count_by_grade['Grade'], count_by_grade['Nombre de Candidats'], color=colors)
                ax.set_title('Répartition des Candidats par Grade', fontsize=14, fontweight='bold')
                ax.set_ylabel('Nombre de Candidats')
                plt.xticks(rotation=45)
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom')
                
                st.pyplot(fig)
            
            with col2:
                # Compter les candidats par vicariat
                count_by_vicariat = self.df_candidats['vicariat'].value_counts().reset_index()
                count_by_vicariat.columns = ['Vicariat', 'Nombre de Candidats']
                
                st.write("**Nombre de candidats par vicariat:**")
                st.dataframe(count_by_vicariat, use_container_width=True)
                
                # Graphique circulaire pour les vicariats
                fig, ax = plt.subplots(figsize=(8, 8))
                colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFD700', '#FF69B4']
                wedges, texts, autotexts = ax.pie(count_by_vicariat['Nombre de Candidats'], 
                                                labels=count_by_vicariat['Vicariat'],
                                                autopct='%1.1f%%', colors=colors, startangle=90)
                ax.set_title('Répartition des Candidats par Vicariat', fontsize=14, fontweight='bold')
                
                # Améliorer l'apparence
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                st.pyplot(fig)
            
        else:
            st.info("Aucune donnée de candidats disponible")
    
    def afficher_resultats_par_grade(self):
        """Afficher les résultats par grade avec des tableaux"""
        st.subheader("📊 Distribution des Notes par Grade")
        
        if not self.df_resultats.empty and 'moyenne' in self.df_resultats.columns:
            # Statistiques détaillées
            st.write("**Statistiques détaillées par grade:**")
            stats = self.df_resultats.groupby('grade')['moyenne'].agg([
                ('Nombre', 'count'),
                ('Moyenne', 'mean'),
                ('Médiane', 'median'),
                ('Ecart-type', 'std'),
                ('Minimum', 'min'),
                ('Maximum', 'max')
            ]).round(2)
            
            # Réorganiser selon l'ordre défini
            stats = stats.reindex(GRADES_ORDRE)
            st.dataframe(stats)
            
            # Interprétation des statistiques
            self.afficher_interpretation_statistiques(stats)
            
            # Graphique des moyennes par grade
            st.write("**Moyennes par grade:**")
            fig, ax = plt.subplots(figsize=(12, 6))
            moyennes_par_grade = self.df_resultats.groupby('grade')['moyenne'].mean().round(2)
            moyennes_par_grade = moyennes_par_grade.reindex(GRADES_ORDRE)
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            bars = ax.bar(moyennes_par_grade.index, moyennes_par_grade.values, color=colors)
            ax.axhline(y=12, color='red', linestyle='--', alpha=0.7, label='Seuil de validation (12)')
            ax.set_title('Moyennes des Notes par Grade', fontsize=14, fontweight='bold')
            ax.set_ylabel('Moyenne')
            ax.legend()
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig)
            
            # Afficher la répartition des décisions
            if 'decision' in self.df_resultats.columns:
                st.write("**Répartition des décisions par grade:**")
                decisions_par_grade = pd.crosstab(self.df_resultats['grade'], self.df_resultats['decision'])
                decisions_par_grade = decisions_par_grade.reindex(GRADES_ORDRE)
                st.dataframe(decisions_par_grade)
                
                # Graphique des décisions
                fig, ax = plt.subplots(figsize=(12, 6))
                decisions_par_grade.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4', '#96CEB4'])
                ax.set_title('Répartition des Décisions par Grade', fontsize=14, fontweight='bold')
                ax.set_ylabel('Nombre de Candidats')
                ax.legend(title='Décision')
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
                # Interprétation des décisions
                self.afficher_interpretation_decisions(decisions_par_grade)
            
        else:
            st.info("Aucun résultat disponible")
    
    def afficher_interpretation_statistiques(self, stats):
        """Afficher l'interprétation des statistiques en termes simples"""
        st.subheader("🎯 Interprétation des Résultats")
        
        # Analyser chaque grade
        for grade in stats.index:
            if grade in stats.index:
                data = stats.loc[grade]
                moyenne = data['Moyenne']
                ecart_type = data['Ecart-type']
                min_note = data['Minimum']
                max_note = data['Maximum']
                nombre = data['Nombre']
                
                st.write(f"**Grade {grade}:**")
                
                # Interprétation de la moyenne
                if moyenne >= 16:
                    st.success("🎯 **Excellente performance** - La majorité des candidats maîtrisent très bien les compétences")
                elif moyenne >= 14:
                    st.info("✅ **Bonne performance** - Les candidats ont globalement réussi")
                elif moyenne >= 12:
                    st.warning("⚠️ **Performance moyenne** - Des efforts supplémentaires sont nécessaires")
                else:
                    st.error("❌ **Performance faible** - Nécessite une révision du programme de formation")
                
                # Interprétation de l'écart-type
                if ecart_type < 2:
                    st.info("📏 **Homogénéité** - Les résultats sont très regroupés, peu de différences entre candidats")
                elif ecart_type < 4:
                    st.info("📐 **Dispersion modérée** - Différences acceptables entre les candidats")
                else:
                    st.warning("📈 **Forte dispersion** - Grandes différences de niveau entre candidats")
                
                # Écart entre min et max
                ecart_min_max = max_note - min_note
                if ecart_min_max > 10:
                    st.warning("⚡ **Grand écart de niveau** - Certains candidats excellent tandis que d'autres sont en difficulté")
                
                st.write("---")
    
    def afficher_interpretation_decisions(self, decisions_par_grade):
        """Afficher l'interprétation des décisions"""
        st.subheader("🎓 Analyse des Résultats par Grade")
        
        for grade in decisions_par_grade.index:
            if grade in decisions_par_grade.index:
                data = decisions_par_grade.loc[grade]
                total = data.sum()
                # Compter Admis et Admis_Passe au grade immédiatement supérieur comme admis
                admis = data.get('Admis', 0) + data.get('Admis_Passe au grade immédiatement supérieur', 0)
                taux_admis = (admis / total * 100) if total > 0 else 0
                
                st.write(f"**Grade {grade}:**")
                st.write(f"- {admis}/{total} admis ({taux_admis:.1f}%)")
                
                if taux_admis >= 80:
                    st.success("🏆 **Excellent taux de réussite** - La formation est très bien assimilée")
                elif taux_admis >= 60:
                    st.info("✅ **Bon taux de réussite** - La majorité des candidats atteignent les objectifs")
                elif taux_admis >= 40:
                    st.warning("⚠️ **Taux de réussite modéré** - Certains aspects méritent d'être revus")
                else:
                    st.error("❌ **Taux de réussite faible** - Nécessite une analyse approfondie des difficultés")
                
                st.write("---")
    
    def afficher_classement(self):
        """Afficher le classement général"""
        st.subheader("🏆 Classement Général")
        
        if not self.df_resultats.empty and 'moyenne' in self.df_resultats.columns:
            # Fusionner avec les données des candidats pour avoir TOUTES les informations
            df_classement_complet = self.df_resultats.merge(
                self.df_candidats[['matricule', 'nom', 'prenom', 'grade', 'vicariat']], 
                on='matricule', 
                how='left',
                suffixes=('', '_candidat')
            )
            
            # Utiliser les colonnes fusionnées
            if 'nom_candidat' in df_classement_complet.columns:
                df_classement_complet['nom'] = df_classement_complet['nom_candidat']
            if 'prenom_candidat' in df_classement_complet.columns:
                df_classement_complet['prenom'] = df_classement_complet['prenom_candidat']
            if 'grade_candidat' in df_classement_complet.columns:
                df_classement_complet['grade'] = df_classement_complet['grade_candidat']
            if 'vicariat_candidat' in df_classement_complet.columns:
                df_classement_complet['vicariat'] = df_classement_complet['vicariat_candidat']
            
            df_classement = df_classement_complet.sort_values(['grade', 'rang'])
            
            # Ajouter des filtres
            col1, col2 = st.columns(2)
            with col1:
                grade_selectionne = st.selectbox(
                    "Filtrer par grade:",
                    ["Tous"] + list(df_classement['grade'].unique())
                )
            with col2:
                vicariat_selectionne = st.selectbox(
                    "Filtrer par vicariat:",
                    ["Tous"] + list(df_classement['vicariat'].unique())
                )
            
            if grade_selectionne != "Tous":
                df_classement = df_classement[df_classement['grade'] == grade_selectionne]
            
            if vicariat_selectionne != "Tous":
                df_classement = df_classement[df_classement['vicariat'] == vicariat_selectionne]
            
            # Sélectionner les colonnes disponibles
            colonnes_disponibles = []
            for col in ['matricule', 'nom', 'prenom', 'grade', 'vicariat', 'moyenne', 'rang', 'mention', 'decision']:
                if col in df_classement.columns:
                    colonnes_disponibles.append(col)
            
            st.dataframe(
                df_classement[colonnes_disponibles],
                use_container_width=True
            )
            
            # Télécharger le classement
            csv_classement = df_classement[colonnes_disponibles].to_csv(index=False)
            st.download_button(
                label="📥 Télécharger le classement",
                data=csv_classement,
                file_name=f"classement_{self.activite}_{datetime.now().year}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucun résultat à afficher")
    
    def generer_rapport_excel(self):
        """Générer un rapport Excel complet"""
        try:
            nom_fichier = f"rapport_{self.activite}_{datetime.now().year}.xlsx"
            with pd.ExcelWriter(nom_fichier, engine='openpyxl') as writer:
                self.df_candidats.to_excel(writer, sheet_name='Candidats', index=False)
                
                if not self.df_resultats.empty:
                    self.df_resultats.to_excel(writer, sheet_name='Résultats', index=False)
                    
                    # Statistiques par grade
                    if 'moyenne' in self.df_resultats.columns and 'decision' in self.df_resultats.columns:
                        stats = self.df_resultats.groupby('grade').agg({
                            'moyenne': ['mean', 'median', 'std', 'min', 'max'],
                            'decision': lambda x: ((x == 'Admis') | (x == 'Admis_Passe au grade immédiatement supérieur')).sum()
                        }).round(2)
                        stats.to_excel(writer, sheet_name='Statistiques')
                
                return nom_fichier
        except Exception as e:
            st.error(f"Erreur lors de la génération du rapport: {e}")
            return None

    def generer_rapport_pdf(self):
        """Générer un rapport PDF complet avec graphiques"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib import colors
            import matplotlib.pyplot as plt
            from io import BytesIO
            import tempfile
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centré
            )
            
            # En-tête CENTRÉ
            elements.append(Paragraph("ARCHIDIOCESE DE COTONOU", styles['Heading2']))
            elements.append(Paragraph("COMMUNAUTE DIOCESAINE DES LECTEURS JUNIORS", styles['Heading2']))
            elements.append(Paragraph(f"WEEK-END DE FORMATION DES ANIMATEURS {datetime.now().year}", styles['Heading2']))
            elements.append(Paragraph("RAPPORT DU WEEK-END DE FORMATION DES ANIMATEURS", title_style))
            elements.append(Spacer(1, 1*cm))
            
            # Introduction
            total_candidats = len(self.df_candidats)
            paroisses = self.df_candidats['paroisse'].nunique()
            vicariats = self.df_candidats['vicariat'].nunique()
            femmes = len(self.df_candidats[self.df_candidats['genre'] == 'F'])
            hommes = len(self.df_candidats[self.df_candidats['genre'] == 'M'])
            
            intro_text = f"""
            Pour le compte du Week-End de Formation des Animateurs, nous avons accueilli cette année un nombre total de <b>{total_candidats}</b> candidats répartis selon les différents grades.
            
            Ces participants provenaient de <b>{paroisses}</b> paroisses, représentant <b>{vicariats}</b> vicariats.
            Chaque paroisse a contribué à la richesse de cette formation par la présence de ses animateurs engagés.
            
            La répartition des participants selon le sexe fait état de <b>{femmes}</b> femmes et <b>{hommes}</b> hommes, témoignant d'une participation équilibrée et inclusive.
            """
            
            elements.append(Paragraph(intro_text, styles['Normal']))
            elements.append(Spacer(1, 1*cm))
            
            # AJOUT DES GRAPHIQUES DANS LE PDF
            if not self.df_resultats.empty:
                # Graphique 1: Répartition par grade
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                count_by_grade = self.df_candidats['grade'].value_counts().reindex(GRADES_ORDRE)
                colors_chart = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                bars = ax1.bar(count_by_grade.index, count_by_grade.values, color=colors_chart)
                ax1.set_title('Répartition des Candidats par Grade', fontsize=12, fontweight='bold')
                ax1.set_ylabel('Nombre de Candidats')
                plt.xticks(rotation=45)
                
                # Sauvegarder le graphique temporairement
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp1:
                    plt.tight_layout()
                    plt.savefig(tmp1.name, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    # Ajouter l'image au PDF
                    elements.append(Paragraph("Répartition des Candidats par Grade", styles['Heading3']))
                    elements.append(Image(tmp1.name, width=15*cm, height=10*cm))
                    elements.append(Spacer(1, 0.5*cm))
                
                # Graphique 2: Moyennes par grade
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                moyennes_par_grade = self.df_resultats.groupby('grade')['moyenne'].mean().round(2).reindex(GRADES_ORDRE)
                bars = ax2.bar(moyennes_par_grade.index, moyennes_par_grade.values, color=colors_chart)
                ax2.axhline(y=12, color='red', linestyle='--', alpha=0.7, label='Seuil de validation (12)')
                ax2.set_title('Moyennes des Notes par Grade', fontsize=12, fontweight='bold')
                ax2.set_ylabel('Moyenne')
                ax2.legend()
                plt.xticks(rotation=45)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp2:
                    plt.tight_layout()
                    plt.savefig(tmp2.name, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    elements.append(Paragraph("Moyennes des Notes par Grade", styles['Heading3']))
                    elements.append(Image(tmp2.name, width=15*cm, height=10*cm))
                    elements.append(Spacer(1, 0.5*cm))
        
        # RÉSULTATS PAR GRADE - CORRECTION CRITIQUE
            if not self.df_resultats.empty:
            # CRÉATION D'UN DATAFRAME COMPLET AVEC VICARIAT
            # Fusionner les résultats avec les données candidats pour avoir le vicariat
             df_resultats_complet = self.df_resultats.merge(
                self.df_candidats[['matricule', 'nom', 'prenom', 'vicariat']], 
                on='matricule', 
                how='left',
                suffixes=('', '_candidat')
            )
            
            # VÉRIFICATION ET CORRECTION DE LA COLONNE VICARIAT
            if 'vicariat_candidat' in df_resultats_complet.columns:
                df_resultats_complet['vicariat'] = df_resultats_complet['vicariat_candidat']
            
            # Vérifier que la colonne vicariat existe
            if 'vicariat' not in df_resultats_complet.columns:
                # Si vicariat n'existe pas, essayer de le récupérer des candidats
                df_temp = self.df_resultats[['matricule']].merge(
                    self.df_candidats[['matricule', 'vicariat']],
                    on='matricule',
                    how='left'
                )
                df_resultats_complet['vicariat'] = df_temp['vicariat']
            
            # Si toujours pas de vicariat, utiliser une valeur par défaut
            if 'vicariat' not in df_resultats_complet.columns:
                df_resultats_complet['vicariat'] = "Non spécifié"
                st.warning("Colonne 'vicariat' non trouvée, utilisation de valeur par défaut")
            
            # Considérer Admis et Admis_Passe au grade immédiatement supérieur comme "Admis"
            df_resultats_complet['decision_simple'] = df_resultats_complet['decision'].replace(
                {'Admis_Passe au grade immédiatement supérieur': 'Admis'}
            )
            
            total_admis = len(df_resultats_complet[df_resultats_complet['decision_simple'] == 'Admis'])
            total_ajournes = len(df_resultats_complet[df_resultats_complet['decision_simple'] == 'Échec'])
            
            resultats_text = f"""
            À l'issue des évaluations, <b>{total_admis}</b> candidats ont été admis contre <b>{total_ajournes}</b> non admis.
            Les résultats détaillés par grade montrent que :
            """
            elements.append(Paragraph(resultats_text, styles['Normal']))
            
            # Tableau des résultats par grade
            resultats_grade = df_resultats_complet.groupby('grade')['decision_simple'].value_counts().unstack(fill_value=0)
            resultats_grade = resultats_grade.reindex(GRADES_ORDRE)
            
            table_data = [['Grade', 'Admis', 'Échec']]
            for grade in GRADES_ORDRE:
                if grade in resultats_grade.index:
                    admis = resultats_grade.loc[grade].get('Admis', 0)
                    ajournes = resultats_grade.loc[grade].get('Échec', 0)
                    table_data.append([grade, admis, ajournes])
                else:
                    table_data.append([grade, 0, 0])
            
            table = Table(table_data, colWidths=[4*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 1*cm))
            
            # NOUVELLE SECTION: RÉSULTATS PAR VICARIAT ET GRADE
            elements.append(Paragraph("RÉSULTATS DÉTAILLÉS PAR VICARIAT ET GRADE", styles['Heading3']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Obtenir tous les vicariats disponibles depuis df_candidats (qui contient les bonnes données)
            try:
                vicariats_list = sorted(self.df_candidats['vicariat'].dropna().unique())
                if not vicariats_list:
                    vicariats_list = ["Données non disponibles"]
                st.info(f"Vicariats utilisés pour le PDF: {vicariats_list}")
            except Exception as e:
                st.warning(f"Impossible de récupérer les vicariats: {e}")
                vicariats_list = ["Données non disponibles"]
            
            for vicariat in vicariats_list:
                elements.append(Paragraph(f"Vicariat: {vicariat}", styles['Heading4']))
                
                # Filtrer les résultats pour le vicariat actuel
                # Utiliser df_resultats_complet qui contient maintenant le vicariat
                df_vicariat = df_resultats_complet[df_resultats_complet['vicariat'] == vicariat]
                
                # Tableau des résultats par grade pour ce vicariat
                try:
                    resultats_vicariat_grade = df_vicariat.groupby('grade')['decision_simple'].value_counts().unstack(fill_value=0)
                    
                    table_data_vicariat = [['Grade', 'Admis', 'Échec', 'Total', 'Taux Réussite']]
                    for grade in GRADES_ORDRE:
                        if grade in resultats_vicariat_grade.index:
                            admis = resultats_vicariat_grade.loc[grade].get('Admis', 0)
                            ajournes = resultats_vicariat_grade.loc[grade].get('Échec', 0)
                            total_grade = admis + ajournes
                            taux_reussite = (admis / total_grade * 100) if total_grade > 0 else 0
                            table_data_vicariat.append([
                                grade, 
                                admis, 
                                ajournes, 
                                total_grade,
                                f"{taux_reussite:.1f}%"
                            ])
                        else:
                            table_data_vicariat.append([grade, 0, 0, 0, "0%"])
                    
                    # Totaux pour le vicariat
                    total_vicariat_admis = len(df_vicariat[df_vicariat['decision_simple'] == 'Admis'])
                    total_vicariat_ajournes = len(df_vicariat[df_vicariat['decision_simple'] == 'Échec'])
                    total_vicariat = len(df_vicariat)
                    taux_reussite_vicariat = (total_vicariat_admis / total_vicariat * 100) if total_vicariat > 0 else 0
                    
                    table_data_vicariat.append([
                        'TOTAL', 
                        total_vicariat_admis, 
                        total_vicariat_ajournes, 
                        total_vicariat,
                        f"{taux_reussite_vicariat:.1f}%"
                    ])
                    
                    table_vicariat = Table(table_data_vicariat, colWidths=[3*cm, 2*cm, 2*cm, 2*cm, 3*cm])
                    table_vicariat.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -2), colors.lightblue),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),
                        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(table_vicariat)
                    elements.append(Spacer(1, 0.5*cm))
                    
                except Exception as e:
                    elements.append(Paragraph(f"Erreur lors du traitement des données pour {vicariat}: {str(e)}", styles['Normal']))
                    elements.append(Spacer(1, 0.5*cm))
        
        # Conclusion
            conclusion_text = """
        L'analyse statistique effectuée par paroisse et par vicariat met en évidence le niveau de performance des différents groupes.
        Certains vicariats se distinguent particulièrement par leurs taux d'admission élevés, traduisant la qualité du suivi et de la préparation des candidats.
        
        En somme, cette édition du Week-End de Formation des Animateurs se révèle très enrichissante tant sur le plan de la participation que sur celui des résultats obtenus, marquant une étape importante dans la dynamique de formation et d'engagement des jeunes animateurs au sein de notre diocèse.
        """
            elements.append(Paragraph(conclusion_text, styles['Normal']))
            elements.append(Spacer(1, 2*cm))
        
        # Pied de page
            elements.append(Paragraph("Lecteurs, Sel et Lumière nous sommes", styles['Normal']))
        
            doc.build(elements)
            buffer.seek(0)
            return buffer
        
        except Exception as e:
            st.error(f"Erreur lors de la génération du rapport PDF: {e}")
            import traceback
            st.error(f"Détails: {traceback.format_exc()}")
            return None

# Le reste du code reste inchangé...

class CorrecteurCompositions:
    def __init__(self, activite):
        self.seuil_reussite = 12
        self.seuil_excellence = 16
        self.activite = activite
    
    def importer_notes(self, fichier_notes):
        """Importer le fichier Excel des notes avec TOUTES les feuilles"""
        try:
            # Augmenter la capacité d'importation
            import warnings
            warnings.filterwarnings('ignore')
            
            # Lire toutes les feuilles
            excel_file = pd.ExcelFile(fichier_notes)
            all_sheets_data = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    # Utiliser des paramètres optimisés pour les gros fichiers
                    notes_df = pd.read_excel(
                        fichier_notes, 
                        sheet_name=sheet_name,
                        engine='openpyxl',
                        dtype={'matricule': str}  # Forcer le matricule en texte
                    )
                    
                    # Nettoyer les noms de colonnes
                    notes_df.columns = notes_df.columns.str.strip()
                    
                    # Vérifier les colonnes requises
                    colonnes_requises = ['matricule', 'COMPO1', 'COMPO2', 'COMPO3', 'COMPO4', 'COMPO5']
                    colonnes_presentes = [col for col in colonnes_requises if col in notes_df.columns]
                    
                    if len(colonnes_presentes) >= 2:  # Au moins matricule et une note
                        # Nettoyer les données
                        notes_df = notes_df.dropna(subset=['matricule'])
                        notes_df['matricule'] = notes_df['matricule'].astype(str).str.strip()
                        
                        # Calculer la moyenne des compositions disponibles
                        colonnes_notes = [col for col in ['COMPO1', 'COMPO2', 'COMPO3', 'COMPO4', 'COMPO5'] if col in notes_df.columns]
                        
                        # Convertir les notes en numérique, gérer les erreurs
                        for col in colonnes_notes:
                            notes_df[col] = pd.to_numeric(notes_df[col], errors='coerce')
                        
                        notes_df['note'] = notes_df[colonnes_notes].mean(axis=1).round(2)
                        
                        # Filtrer les lignes avec des notes valides
                        notes_df = notes_df.dropna(subset=['note'])
                        
                        if not notes_df.empty:
                            all_sheets_data.append(notes_df[['matricule', 'note']])
                            st.success(f"✅ Feuille '{sheet_name}' importée: {len(notes_df)} notes valides")
                        else:
                            st.warning(f"⚠️ Feuille '{sheet_name}' ignorée: aucune note valide")
                    else:
                        st.warning(f"⚠️ Feuille '{sheet_name}' ignorée: colonnes insuffisantes")
                        
                except Exception as e:
                    st.warning(f"⚠️ Erreur avec la feuille '{sheet_name}': {str(e)}")
            
            if all_sheets_data:
                # Combiner toutes les données
                combined_df = pd.concat(all_sheets_data, ignore_index=True)
                
                # Supprimer les doublons (garder la dernière occurrence)
                combined_df = combined_df.drop_duplicates(subset=['matricule'], keep='last')
                
                st.success(f"🎉 Import terminé: {len(combined_df)} notes uniques provenant de {len(all_sheets_data)} feuille(s)")
                return combined_df
            else:
                st.error("❌ Aucune donnée valide trouvée dans le fichier")
                return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Erreur lors de l'importation du fichier: {str(e)}")
            import traceback
            st.error(f"Détails: {traceback.format_exc()}")
            return pd.DataFrame()
    
    def calculer_moyennes(self, notes_df):
        """Calculer les moyennes pour chaque candidat"""
        if notes_df.empty:
            return pd.DataFrame()
        
        # Grouper par matricule et calculer la moyenne
        moyennes_df = notes_df.groupby('matricule').agg({
            'note': 'mean'
        }).round(2).reset_index()
        
        return moyennes_df
    
    def determiner_mention(self, moyenne):
        """Déterminer la mention selon la moyenne (NOUVEAU BARÈME)"""
        if moyenne >= 16:
            return "T.Bien"
        elif moyenne >= 14:
            return "Bien"
        elif moyenne >= 12:
            return "A.Bien"
        else:
            return "Passable"
    
    def determiner_decision(self, moyenne, grade):
        """Déterminer la décision selon la moyenne et le grade (NOUVEAU BARÈME)"""
        if moyenne >= self.seuil_reussite:
            if grade == 'Formation 2':
                return "Admis"  # Dernier grade, juste "Admis"
            else:
                return "Admis_Passe au grade immédiatement supérieur"
        else:
            return "Échec"  # Redouble
    
    def proclamer_resultats(self, notes_df, df_candidats):
        """Proclamer les résultats avec classement PAR GRADE"""
        if notes_df.empty:
            return pd.DataFrame()
        
        moyennes_df = self.calculer_moyennes(notes_df)
        
        if moyennes_df.empty:
            return pd.DataFrame()
        
        # Fusionner avec les informations des candidats
        resultats_df = moyennes_df.merge(
            df_candidats[['matricule', 'nom', 'prenom', 'grade', 'vicariat']],
            on='matricule',
            how='left'
        )
            
        resultats = []
        
        for grade in GRADES_ORDRE:
            if grade in resultats_df['grade'].unique():
                df_grade = resultats_df[resultats_df['grade'] == grade].copy()
                df_grade = df_grade.sort_values('note', ascending=False)
                df_grade['rang'] = range(1, len(df_grade) + 1)
                
                for _, row in df_grade.iterrows():
                    mention = self.determiner_mention(row['note'])
                    decision = self.determiner_decision(row['note'], row['grade'])
                    
                    resultats.append({
                        'matricule': row['matricule'],
                        'nom': row['nom'],
                        'prenom': row['prenom'],
                        'grade': grade,
                        'vicariat': row['vicariat'],
                        'moyenne': row['note'],
                        'rang': int(row['rang']),
                        'mention': mention,
                        'decision': decision
                    })
        
        return pd.DataFrame(resultats)
    
    def afficher_analyse_notes(self, notes_df):
        """Afficher une analyse détaillée des notes"""
        if notes_df.empty:
            return
        
        st.subheader("📈 Analyse Détaillée des Notes")
        
        stats = notes_df['note'].describe()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Moyenne Générale", f"{stats['mean']:.2f}")
        with col2:
            st.metric("Médiane", f"{stats['50%']:.2f}")
        with col3:
            st.metric("Écart-type", f"{stats['std']:.2f}")
        with col4:
            st.metric("Nombre de Notes", int(stats['count']))
        
        st.write("### 🎯 Interprétation Générale")
        
        moyenne = stats['mean']
        mediane = stats['50%']
        ecart_type = stats['std']
        
        if moyenne >= 14:
            st.success("**Performance globale excellente** - Les candidats maîtrisent bien les compétences évaluées")
        elif moyenne >= 12:
            st.info("**Performance globale satisfaisante** - Niveau acceptable avec quelques points à améliorer")
        elif moyenne >= 10:
            st.warning("**Performance globale modérée** - Des efforts supplémentaires sont nécessaires")
        else:
            st.error("**Performance globale faible** - Révision nécessaire du programme de formation")
        
        if abs(moyenne - mediane) > 1:
            st.info("📊 **Distribution asymétrique** - La présence de notes extrêmes influence la moyenne")
        else:
            st.info("📊 **Distribution équilibrée** - Les notes sont réparties de manière homogène")
        
        if ecart_type < 3:
            st.success("🎯 **Faible dispersion** - Niveau homogène entre les candidats")
        elif ecart_type < 5:
            st.info("📐 **Dispersion modérée** - Différences acceptables entre candidats")
        else:
            st.warning("⚡ **Forte dispersion** - Grands écarts de niveau entre candidats")

def generer_matricule(nom, grade, ordre, annee_courante=None):
    if annee_courante is None:
        annee_courante = datetime.now().year
    
    initiales_grade = {
        'Animation 1': 'AN1', 'Animation 2': 'AN2', 
        'Formation 1': 'FO1', 'Formation 2': 'FO2',
        'Lectorat 2': 'LE2'
    }
    
    init_grade = initiales_grade.get(grade, 'XX')
    annee = str(annee_courante)[-2:]
    
    return f"{ordre:03d}-{init_grade}-{annee}"

def assigner_matricules(df):
    """Assigner les matricules en évitant les doublons"""
    df_unique = df.drop_duplicates(subset=['nom', 'prenom', 'grade'])
    df_sorted = df_unique.sort_values(['nom', 'prenom'])
    annee_courante = datetime.now().year
    
    matricules = []
    for grade in GRADES_ORDRE:
        if grade in df_sorted['grade'].unique():
            df_grade = df_sorted[df_sorted['grade'] == grade].copy()
            df_grade = df_grade.reset_index(drop=True)
            
            for idx, row in df_grade.iterrows():
                matricule = generer_matricule(row['nom'], row['grade'], idx + 1, annee_courante)
                matricules.append({
                    'nom': row['nom'], 
                    'prenom': row['prenom'], 
                    'matricule': matricule, 
                    'grade': row['grade']
                })
    
    return pd.DataFrame(matricules)

def ajouter_candidat_manuel(df_existant):
    """Interface pour ajouter manuellement un candidat en retard"""
    st.subheader("➕ Ajouter un candidat en retard")
    
    with st.form("form_ajout_candidat"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom *")
            prenom = st.text_input("Prénom *")
            grade = st.selectbox("Grade *", GRADES_ORDRE)
        
        with col2:
            genre = st.selectbox("Genre *", ["M", "F"])
            date_naissance = st.date_input("Date de naissance *")
            paroisse = st.selectbox("Paroisse *", list(set([p for paroisses in VICARIATS.values() for p in paroisses])))
        
        submitted = st.form_submit_button("Ajouter le candidat")
        
        if submitted:
            if not all([nom, prenom, grade, genre, paroisse]):
                st.error("Veuillez remplir tous les champs obligatoires (*)")
                return df_existant
            
            # Vérifier si le candidat existe déjà
            existe = ((df_existant['nom'] == nom) & (df_existant['prenom'] == prenom) & (df_existant['grade'] == grade)).any()
            if existe:
                st.error("Ce candidat existe déjà dans la base de données")
                return df_existant
            
            # Générer le matricule
            df_grade = df_existant[df_existant['grade'] == grade]
            nouvel_ordre = len(df_grade) + 1
            matricule = generer_matricule(nom, grade, nouvel_ordre)
            
            # Ajouter le nouveau candidat
            nouveau_candidat = {
                'nom': nom,
                'prenom': prenom,
                'grade': grade,
                'genre': genre,
                'date_naissance': date_naissance.strftime('%d/%m/%Y'),
                'paroisse': paroisse,
                'matricule': matricule,
                'vicariat': determiner_vicariat(paroisse)
            }
            
            df_existant = pd.concat([df_existant, pd.DataFrame([nouveau_candidat])], ignore_index=True)
            st.success(f"✅ Candidat ajouté avec succès ! Matricule : {matricule}")
            
            return df_existant
    
    return df_existant

def generer_fichier_notes_pdf(df_candidats):
    """Générer un fichier PDF avec la liste des matricules par grade"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # CENTRÉ
        )
        
        # En-tête CENTRÉ
        elements.append(Paragraph("ARCHIDIOCESE DE COTONOU", styles['Heading2']))
        elements.append(Paragraph("COMMUNAUTE DIOCESAINE DES LECTEURS JUNIORS", styles['Heading2']))
        elements.append(Paragraph(f"WEEK-END DE FORMATION DES ANIMATEURS {datetime.now().year}", styles['Heading2']))
        elements.append(Paragraph("MATRICULES PAR GRADE", title_style))
        elements.append(Spacer(1, 1*cm))
        
        # Par grade
        for i, grade in enumerate(GRADES_ORDRE, 1):
            if grade in df_candidats['grade'].unique():
                df_grade = df_candidats[df_candidats['grade'] == grade].sort_values('matricule')
                
                elements.append(Paragraph(f"GRADE {i} : {grade.upper()}", styles['Heading3']))
                elements.append(Spacer(1, 0.5*cm))
                
                # Préparer les données du tableau
                table_data = [['Matricule', 'Nom', 'Prénoms', 'Paroisse', 'Vicariat']]
                for _, row in df_grade.iterrows():
                    table_data.append([
                        row['matricule'],
                        row['nom'],
                        row['prenom'],
                        row['paroisse'],
                        row['vicariat']
                    ])
                
                # Créer le tableau
                table = Table(table_data, colWidths=[3*cm, 3*cm, 4*cm, 3*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 1*cm))
        
        # Pied de page
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("Lecteurs, Sel et Lumière nous sommes", styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF: {e}")
        return None

def generer_fichier_notes_excel(df_candidats):
    """Générer un fichier Excel avec les colonnes COMPO1 à COMPO5 par grade"""
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for grade in GRADES_ORDRE:
            if grade in df_candidats['grade'].unique():
                df_grade = df_candidats[df_candidats['grade'] == grade].sort_values('matricule')
                
                # Créer le DataFrame pour les notes
                df_notes = pd.DataFrame({
                    'matricule': df_grade['matricule'],
                    'COMPO1': '',
                    'COMPO2': '',
                    'COMPO3': '',
                    'COMPO4': '',
                    'COMPO5': ''
                })
                
                # Écrire dans une feuille par grade
                df_notes.to_excel(writer, sheet_name=grade[:31], index=False)
    
    buffer.seek(0)
    return buffer

def importer_fichier_candidats(activite):
    """Importer le fichier des candidats avec gestion améliorée"""
    st.sidebar.header(f"📁 Import des Candidats")
    
    fichier_candidats = st.sidebar.file_uploader(
        f"Importer le fichier Excel des candidats", 
        type=['xlsx'],
        key=f"file_{activite}",
        help="Taille maximale: 200MB. Format requis: nom, prenom, grade, genre, date_naissance, paroisse"
    )
    
    if fichier_candidats is not None:
        try:
            # Utiliser des paramètres optimisés pour les gros fichiers
            df_initial = pd.read_excel(
                fichier_candidats, 
                engine='openpyxl',
                dtype={'nom': str, 'prenom': str, 'grade': str, 'genre': str, 'paroisse': str}
            )
            
            # Nettoyer les noms de colonnes
            df_initial.columns = df_initial.columns.str.strip()
            
            # Afficher les colonnes disponibles pour debug
            st.sidebar.write(f"Colonnes détectées: {list(df_initial.columns)}")
            
            # Détecter et normaliser la colonne vicariat
            df_initial = normaliser_colonne_vicariat(df_initial)
            
            colonnes_requises = ['nom', 'prenom', 'grade', 'genre', 'date_naissance', 'paroisse']
            colonnes_manquantes = [col for col in colonnes_requises if col not in df_initial.columns]
            
            if colonnes_manquantes:
                st.sidebar.error(f"Colonnes manquantes: {', '.join(colonnes_manquantes)}")
                st.sidebar.info(f"Colonnes disponibles: {', '.join(df_initial.columns)}")
                return None
            
            # Nettoyer les données
            df_initial = df_initial.dropna(subset=['nom', 'prenom', 'grade'])
            df_initial['nom'] = df_initial['nom'].str.strip()
            df_initial['prenom'] = df_initial['prenom'].str.strip()
            df_initial['grade'] = df_initial['grade'].str.strip()
            df_initial['paroisse'] = df_initial['paroisse'].str.strip()
                
            st.sidebar.success(f"✅ {len(df_initial)} candidats importés")
            
            # Détecter les vicariats automatiquement
            detecter_vicariats_automatiquement(df_initial)
            
            # Aperçu des données
            with st.sidebar.expander("Aperçu des données importées"):
                st.write(f"Vicariats: {df_initial['vicariat'].unique()}")
                st.write(f"Grades: {df_initial['grade'].unique()}")
                st.write(df_initial.head(3))
                
            return df_initial
            
        except Exception as e:
            st.sidebar.error(f"Erreur lors de l'import: {str(e)}")
            import traceback
            st.sidebar.error(f"Détails: {traceback.format_exc()}")
            return None
    
    return None

def main():
    # Afficher le logo
    afficher_logo()
    
    # Sélection de l'activité
    st.sidebar.header("🎯 Sélection de l'Activité")
    activite = st.sidebar.radio(
        "Choisir l'activité:",
        ["weekend", "session"],
        format_func=lambda x: "🎯 Week-end de Formation" if x == "weekend" else "📚 Session Diocésaine"
    )
    
    # Information sur le déploiement
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **📊 Tableau de Bord CDLJ**
    
    **Version:** 2.0  
    **Année:** {}  
    **Déployé avec ❤️** pour l'Archidiocèse de Cotonou
    """.format(datetime.now().year))
    
    # Import du fichier des candidats pour l'activité sélectionnée
    df_initial = importer_fichier_candidats(activite)
    
    if df_initial is None:
        if activite == "weekend":
            st.info("📋 Veuillez importer le fichier des candidats pour le Week-end de Formation")
        else:
            st.info("📋 Veuillez importer le fichier des candidats pour la Session Diocésaine")
        return
    
    # Générer les matricules
    df_matricules = assigner_matricules(df_initial)
    df_complet = pd.merge(df_initial, df_matricules, on=['nom', 'prenom', 'grade'])
    
    # Afficher les statistiques d'import
    st.sidebar.write(f"**Candidats uniques:** {len(df_complet)}")
    st.sidebar.write(f"**Grades:** {df_complet['grade'].nunique()}")
    st.sidebar.write(f"**Vicariats:** {df_complet['vicariat'].nunique()}")
    
    # Vérifier la présence de vicariat
    if 'vicariat' not in df_complet.columns:
        st.error("❌ La colonne 'vicariat' est manquante dans les données importées")
        st.write("Colonnes disponibles:", list(df_complet.columns))
        return
    
    # Créer l'instance du tableau de bord
    tableau_bord = TableauBordCompositions(df_complet, pd.DataFrame(), activite)
    
    # Afficher l'en-tête de l'activité
    tableau_bord.afficher_entete_activite()
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "🎫 Matricules", "📝 Correction", "🏆 Résultats"])
    
    with tab1:
        st.header("Vue d'ensemble des Candidats")
        tableau_bord.afficher_kpis()
        tableau_bord.afficher_repartition_grades()
        
        st.subheader("Informations Complémentaires")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Répartition par paroisse:**")
            paroisses = df_complet['paroisse'].value_counts()
            st.dataframe(paroisses)
        
        with col2:
            st.write("**Répartition par genre:**")
            genres = df_complet['genre'].value_counts()
            st.dataframe(genres)
    
    with tab2:
        st.header("🎫 Matricules des Candidats")
        
        # Section pour ajouter des candidats en retard
        with st.expander("➕ Ajouter un candidat en retard"):
            df_complet = ajouter_candidat_manuel(df_complet)
        
        st.write(f"**Total: {len(df_complet)} candidats**")
        
        col1, col2 = st.columns(2)
        with col1:
            grade_filtre = st.selectbox(
                "Filtrer par grade:",
                ["Tous"] + GRADES_ORDRE,
                key=f"grade_{activite}"
            )
        with col2:
            paroisse_filtre = st.selectbox(
                "Filtrer par paroisse:",
                ["Toutes"] + list(df_complet['paroisse'].unique()),
                key=f"paroisse_{activite}"
            )
        
        df_filtre = df_complet.copy()
        if grade_filtre != "Tous":
            df_filtre = df_filtre[df_filtre['grade'] == grade_filtre]
        if paroisse_filtre != "Toutes":
            df_filtre = df_filtre[df_filtre['paroisse'] == paroisse_filtre]
        
        st.dataframe(df_filtre[['matricule', 'nom', 'prenom', 'grade', 'paroisse', 'vicariat']], use_container_width=True)
        
        # Boutons de téléchargement
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df_complet.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"matricules_{activite}_{datetime.now().year}.csv",
                mime="text/csv"
            )
        
        with col2:
            excel_buffer = generer_fichier_notes_excel(df_complet)
            if excel_buffer:
                st.download_button(
                    label="📊 Feuilles de notes Excel",
                    data=excel_buffer,
                    file_name=f"feuilles_notes_{activite}_{datetime.now().year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col3:
            pdf_buffer = generer_fichier_notes_pdf(df_complet)
            if pdf_buffer:
                st.download_button(
                    label="📄 Liste PDF complète",
                    data=pdf_buffer,
                    file_name=f"liste_matricules_{activite}_{datetime.now().year}.pdf",
                    mime="application/pdf"
                )
    
    with tab3:
        st.header("📝 Correction des Copies")
        
        st.info("""
        **Import des Notes - Format requis:**
        - Fichier Excel avec les colonnes: `matricule`, `COMPO1`, `COMPO2`, `COMPO3`, `COMPO4`, `COMPO5`
        - **Le système lit maintenant TOUTES les feuilles du fichier Excel**
        - **Capacité augmentée** - Gestion des fichiers volumineux
        - Le système calculera automatiquement la moyenne des 5 compositions
        """)
        
        fichier_notes = st.file_uploader(
            f"Choisir le fichier Excel des notes", 
            type=['xlsx'],
            key=f"notes_{activite}",
            help="Taille maximale: 200MB. Supporte les fichiers avec plusieurs feuilles"
        )
        
        if fichier_notes is not None:
            correcteur = CorrecteurCompositions(activite)
            notes_df = correcteur.importer_notes(fichier_notes)
            
            if not notes_df.empty:
                st.success(f"✅ Fichier importé: {len(notes_df)} notes valides")
                
                st.write("**Aperçu des notes importées:**")
                st.dataframe(notes_df.head())
                
                correcteur.afficher_analyse_notes(notes_df)
                
                df_resultats = correcteur.proclamer_resultats(notes_df, df_complet)
                st.session_state[f'df_resultats_{activite}'] = df_resultats
                
                st.success("✅ Correction terminée !")
                st.write("**Résultats de la correction:**")
                st.dataframe(df_resultats, use_container_width=True)
    
    with tab4:
        st.header("🏆 Proclamation des Résultats")
        
        if f'df_resultats_{activite}' in st.session_state and not st.session_state[f'df_resultats_{activite}'].empty:
            df_resultats = st.session_state[f'df_resultats_{activite}']
            tableau_bord_resultats = TableauBordCompositions(df_complet, df_resultats, activite)
            
            tableau_bord_resultats.afficher_kpis()
            tableau_bord_resultats.afficher_resultats_par_grade()
            tableau_bord_resultats.afficher_classement()
            
            st.subheader("📤 Export des Résultats")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Générer le Rapport Complet Excel"):
                    nom_fichier = tableau_bord_resultats.generer_rapport_excel()
                    if nom_fichier:
                        st.success(f"📁 Rapport Excel généré: {nom_fichier}")
                        
                        # Proposer le téléchargement
                        with open(nom_fichier, "rb") as file:
                            st.download_button(
                                label="📥 Télécharger le rapport Excel",
                                data=file,
                                file_name=nom_fichier,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.error("❌ Erreur lors de la génération du rapport")
            
            with col2:
                csv_resultats = df_resultats.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les résultats (CSV)",
                    data=csv_resultats,
                    file_name=f"resultats_{activite}_{datetime.now().year}.csv",
                    mime="text/csv"
                )
            
            with col3:
                if st.button("📄 Générer Rapport PDF Complet"):
                    with st.spinner("Génération du rapport PDF en cours..."):
                        pdf_buffer = tableau_bord_resultats.generer_rapport_pdf()
                    if pdf_buffer:
                        st.download_button(
                            label="📥 Télécharger le rapport PDF",
                            data=pdf_buffer,
                            file_name=f"rapport_complet_{activite}_{datetime.now().year}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("❌ Erreur lors de la génération du rapport PDF")
        else:
            st.info("ℹ️ Veuillez d'abord importer et corriger les notes dans l'onglet 'Correction'")

if __name__ == "__main__":
    main()