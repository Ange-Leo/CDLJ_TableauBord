import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os

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
        # Essayer différents chemins possibles pour le logo
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
        
        # Si le logo n'est pas trouvé
        st.sidebar.info("ℹ️ Logo CDLJ non trouvé - Utilisation sans logo")
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
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidats", len(self.df_candidats))
        
        with col2:
            if not self.df_resultats.empty and 'decision' in self.df_resultats.columns:
                admis = self.df_resultats[self.df_resultats['decision'] == 'Admis']
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
    
    def afficher_repartition_grades(self):
        """Afficher la répartition par grade avec des tableaux"""
        st.subheader("📈 Répartition des Candidats par Grade")
        
        if not self.df_candidats.empty:
            # Compter les candidats par grade
            count_by_grade = self.df_candidats['grade'].value_counts().reset_index()
            count_by_grade.columns = ['Grade', 'Nombre de Candidats']
            
            # Afficher un tableau avec style
            st.write("**Nombre de candidats par grade:**")
            st.dataframe(count_by_grade, use_container_width=True)
            
            # Afficher un graphique simple avec st.bar_chart
            st.write("**Graphique de répartition:**")
            chart_data = count_by_grade.set_index('Grade')['Nombre de Candidats']
            st.bar_chart(chart_data)
            
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
            st.dataframe(stats)
            
            # Interprétation des statistiques
            self.afficher_interpretation_statistiques(stats)
            
            # Afficher les moyennes par grade sous forme de graphique
            st.write("**Moyennes par grade:**")
            moyennes_par_grade = self.df_resultats.groupby('grade')['moyenne'].mean().round(2)
            st.bar_chart(moyennes_par_grade)
            
            # Afficher la répartition des décisions
            if 'decision' in self.df_resultats.columns:
                st.write("**Répartition des décisions par grade:**")
                decisions_par_grade = pd.crosstab(self.df_resultats['grade'], self.df_resultats['decision'])
                st.dataframe(decisions_par_grade)
                
                # Interprétation des décisions
                self.afficher_interpretation_decisions(decisions_par_grade)
            
        else:
            st.info("Aucun résultat disponible")
    
    def afficher_interpretation_statistiques(self, stats):
        """Afficher l'interprétation des statistiques en termes simples"""
        st.subheader("🎯 Interprétation des Résultats")
        
        # Analyser chaque grade
        for grade in stats.index:
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
            data = decisions_par_grade.loc[grade]
            total = data.sum()
            admis = data.get('Admis', 0)
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
            df_classement = self.df_resultats.sort_values(['grade', 'rang'])
            
            # Ajouter des filtres
            grade_selectionne = st.selectbox(
                "Filtrer par grade:",
                ["Tous"] + list(df_classement['grade'].unique())
            )
            
            if grade_selectionne != "Tous":
                df_classement = df_classement[df_classement['grade'] == grade_selectionne]
            
            st.dataframe(
                df_classement[['matricule', 'nom', 'prenom', 'grade', 'moyenne', 'rang', 'mention', 'decision']],
                use_container_width=True
            )
            
            # Télécharger le classement
            csv_classement = df_classement.to_csv(index=False)
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
                            'decision': lambda x: (x == 'Admis').sum()
                        }).round(2)
                        stats.to_excel(writer, sheet_name='Statistiques')
                
                return nom_fichier
        except Exception as e:
            st.error(f"Erreur lors de la génération du rapport: {e}")
            return None


class CorrecteurCompositions:
    def __init__(self, activite):
        self.seuil_reussite = 12
        self.seuil_excellence = 16
        self.activite = activite
    
    def importer_notes(self, fichier_notes, df_candidats):
        """Importer le fichier Excel des notes et faire le lien avec les matricules"""
        try:
            notes_df = pd.read_excel(fichier_notes)
            
            # Vérifier les colonnes requises
            colonnes_requises_nom = ['nom', 'prenom', 'note']
            colonnes_requises_matricule = ['matricule', 'note']
            
            if all(col in notes_df.columns for col in colonnes_requises_nom):
                notes_df = self.lier_notes_avec_matricules(notes_df, df_candidats)
            elif all(col in notes_df.columns for col in colonnes_requises_matricule):
                pass
            else:
                st.error("Le fichier doit contenir soit 'nom' et 'prenom', soit 'matricule', et 'note'")
                return pd.DataFrame()
            
            return notes_df
        except Exception as e:
            st.error(f"Erreur lors de l'importation du fichier: {e}")
            return pd.DataFrame()
    
    def lier_notes_avec_matricules(self, notes_df, df_candidats):
        """Faire le lien automatique entre nom/prénom et matricule"""
        notes_avec_matricules = pd.merge(
            notes_df, 
            df_candidats[['nom', 'prenom', 'matricule', 'grade']],
            on=['nom', 'prenom'],
            how='left'
        )
        
        notes_sans_matricule = notes_avec_matricules[notes_avec_matricules['matricule'].isna()]
        if not notes_sans_matricule.empty:
            st.warning(f"⚠️ {len(notes_sans_matricule)} note(s) sans candidat correspondant")
        
        notes_valides = notes_avec_matricules[~notes_avec_matricules['matricule'].isna()]
        
        if len(notes_valides) < len(notes_df):
            st.info(f"✅ {len(notes_valides)} note(s) liée(s) avec succès sur {len(notes_df)}")
        
        return notes_valides
    
    def calculer_moyennes(self, notes_df):
        """Calculer les moyennes pour chaque candidat"""
        if notes_df.empty:
            return pd.DataFrame()
        
        moyennes_df = notes_df.groupby(['matricule', 'nom', 'prenom', 'grade']).agg({
            'note': ['mean', 'count']
        }).round(2)
        
        moyennes_df.columns = ['moyenne', 'nombre_notes']
        moyennes_df = moyennes_df.reset_index()
        
        return moyennes_df
    
    def determiner_mention(self, moyenne):
        """Déterminer la mention selon la moyenne"""
        if moyenne >= self.seuil_excellence:
            return "Excellence"
        elif moyenne >= 14:
            return "Très Bien"
        elif moyenne >= 12:
            return "Bien"
        elif moyenne >= self.seuil_reussite:
            return "Assez Bien"
        else:
            return "Échec"
    
    def proclamer_resultats(self, notes_df):
        """Proclamer les résultats avec classement PAR GRADE"""
        if notes_df.empty:
            return pd.DataFrame()
        
        moyennes_df = self.calculer_moyennes(notes_df)
        
        if moyennes_df.empty:
            return pd.DataFrame()
            
        resultats = []
        
        for grade in moyennes_df['grade'].unique():
            df_grade = moyennes_df[moyennes_df['grade'] == grade].copy()
            df_grade = df_grade.sort_values('moyenne', ascending=False)
            df_grade['rang'] = range(1, len(df_grade) + 1)
            
            for _, row in df_grade.iterrows():
                mention = self.determiner_mention(row['moyenne'])
                decision = "Admis" if row['moyenne'] >= self.seuil_reussite else "Ajourné"
                
                resultats.append({
                    'matricule': row['matricule'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'grade': grade,
                    'moyenne': row['moyenne'],
                    'nombre_notes': int(row['nombre_notes']),
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
    for grade in df_sorted['grade'].unique():
        df_grade = df_sorted[df_sorted['grade'] == grade].copy()
        df_grade = df_grade.reset_index(drop=True)
        
        for idx, row in df_grade.iterrows():
            matricule = generer_matricule(row['nom'], row['grade'], idx + 1, annee_courante)
            matricules.append({
                'nom': row['nom'], 'prenom': row['prenom'], 
                'matricule': matricule, 'grade': row['grade']
            })
    
    return pd.DataFrame(matricules)


def importer_fichier_candidats(activite):
    """Importer le fichier des candidats"""
    st.sidebar.header(f"📁 Import des Candidats")
    
    fichier_candidats = st.sidebar.file_uploader(
        f"Importer le fichier Excel des candidats", 
        type=['xlsx'],
        key=f"file_{activite}"
    )
    
    if fichier_candidats is not None:
        try:
            df_initial = pd.read_excel(fichier_candidats)
            
            colonnes_requises = ['nom', 'prenom', 'grade', 'genre', 'date_naissance', 'paroisse']
            colonnes_manquantes = [col for col in colonnes_requises if col not in df_initial.columns]
            
            if colonnes_manquantes:
                st.sidebar.error(f"Colonnes manquantes: {', '.join(colonnes_manquantes)}")
                return None
                
            st.sidebar.success(f"✅ {len(df_initial)} candidats importés")
            return df_initial
            
        except Exception as e:
            st.sidebar.error(f"Erreur lors de l'import: {e}")
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
    
    **Version:** 1.0  
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
        st.write(f"**Total: {len(df_complet)} candidats**")
        
        col1, col2 = st.columns(2)
        with col1:
            grade_filtre = st.selectbox(
                "Filtrer par grade:",
                ["Tous"] + list(df_complet['grade'].unique()),
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
        
        st.dataframe(df_filtre[['matricule', 'nom', 'prenom', 'grade', 'paroisse']], use_container_width=True)
        
        csv = df_complet.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger la liste des matricules",
            data=csv,
            file_name=f"matricules_{activite}_{datetime.now().year}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.header("📝 Correction des Copies")
        
        if activite == "weekend":
            st.info("""
            **🎯 Week-end de Formation - Import des Notes**
            
            **Format accepté :**
            - Colonnes: `nom`, `prenom`, `note` 
            - OU: `matricule`, `note`
            
            **Le système fera automatiquement le lien avec les matricules !**
            """)
        else:
            st.info("""
            **📚 Session Diocésaine - Import des Notes**
            
            **Format accepté :**
            - Colonnes: `nom`, `prenom`, `note`
            - OU: `matricule`, `note`
            
            **Le système fera automatiquement le lien avec les matricules !**
            """)
        
        fichier_notes = st.file_uploader(
            f"Choisir le fichier Excel des notes", 
            type=['xlsx'],
            key=f"notes_{activite}"
        )
        
        if fichier_notes is not None:
            correcteur = CorrecteurCompositions(activite)
            notes_df = correcteur.importer_notes(fichier_notes, df_complet)
            
            if not notes_df.empty:
                st.success(f"✅ Fichier importé: {len(notes_df)} notes valides")
                
                st.write("**Aperçu des notes importées:**")
                st.dataframe(notes_df[['matricule', 'nom', 'prenom', 'grade', 'note']].head())
                
                correcteur.afficher_analyse_notes(notes_df)
                
                df_resultats = correcteur.proclamer_resultats(notes_df)
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
            col1, col2 = st.columns(2)
            
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
        else:
            st.info("ℹ️ Veuillez d'abord importer et corriger les notes dans l'onglet 'Correction'")


if __name__ == "__main__":
    main()