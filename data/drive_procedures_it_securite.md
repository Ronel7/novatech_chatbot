# Procédures IT & Sécurité informatique — NovaTech SAS
**Google Drive Partagé > NovaTech Internal > DSI > Politiques & Procédures**
_Document : DSI-SEC-2025-v3 | Responsable : Luca Ferrari, RSSI | Approuvé : 15 janvier 2025_
_Classification : INTERNE — Diffusion restreinte aux collaborateurs NovaTech_

---

## Sommaire

1. Accès aux systèmes et gestion des identités
2. Politique des mots de passe
3. Utilisation des appareils (BYOD et équipements NovaTech)
4. Télétravail et accès distant
5. Gestion des données et confidentialité
6. Incidents de sécurité — procédure de signalement
7. Outils autorisés et interdits
8. Formations obligatoires
9. Sanctions et responsabilités

---

## 1. Accès aux systèmes et gestion des identités

### 1.1 Provisionnement des accès

Tout accès aux systèmes NovaTech est provisionné via **Okta** (SSO centralisé). Le provisionnement est déclenché automatiquement par le système RH (Factorial) à la validation du contrat.

**Délais standards :**
- Accès email (@novatech.io) : J-1 avant l'arrivée
- Accès Slack, Notion, GitHub/GitLab : J+0 (jour d'arrivée, session IT onboarding)
- Accès aux environnements de production : J+5 minimum, après formation sécurité validée
- Accès aux données clients : sur demande motivée, validation RSSI + manager

### 1.2 Authentification multi-facteurs (MFA)

La MFA est **obligatoire** sur tous les systèmes NovaTech sans exception. Application recommandée : **Google Authenticator** ou **1Password**. Les SMS comme second facteur sont désactivés depuis le 1er janvier 2025 (risque SIM swapping).

En cas de perte du device MFA : contacter immédiatement **it@novatech.io** — le compte sera suspendu temporairement et rétabli après vérification d'identité en présentiel ou via visioconférence avec pièce d'identité.

### 1.3 Gestion des départs

À la notification de départ (démission, licenciement, fin CDD), la DSI est automatiquement alertée par la DRH. Les accès sont révoqués dans les **24 heures suivant le dernier jour de travail**. Le salarié doit restituer tous les équipements NovaTech avant son dernier jour.

---

## 2. Politique des mots de passe

| Critère | Exigence |
|---------|----------|
| Longueur minimale | 14 caractères |
| Complexité | Majuscules + minuscules + chiffres + caractères spéciaux |
| Durée de validité | 180 jours (rotation forcée) |
| Réutilisation | 12 derniers mots de passe interdits |
| Gestionnaire recommandé | **1Password** (licence fournie par NovaTech) |
| Partage de mots de passe | **Strictement interdit**, y compris entre collègues |

> **Recommandation** : Utilisez des phrases de passe plutôt que des mots de passe (ex. : `Banane!Nuage42-Soleil`). Plus longues, plus mémorables, plus sûres.

---

## 3. Utilisation des appareils

### 3.1 Équipements fournis par NovaTech

Chaque collaborateur reçoit un ordinateur portable (MacBook Pro M3 pour profils techniques, Dell XPS pour autres profils). Ces équipements restent la **propriété de NovaTech** et doivent être restitués à la fin du contrat.

**Règles d'utilisation :**
- Installation de logiciels non autorisés : **interdite**. Toute demande d'installation via le portail IT : it-requests.novatech.io (délai de traitement : 2 jours ouvrés)
- Connexion de périphériques externes (clés USB) : autorisée uniquement après scan antivirus via l'outil **CrowdStrike Falcon** (installé sur tous les postes)
- Transfert de données professionnelles sur cloud personnel (Google Drive perso, Dropbox, WeTransfer) : **interdit**. Utilisez exclusivement les outils approuvés (voir section 7)

### 3.2 BYOD (Bring Your Own Device)

L'utilisation d'appareils personnels pour accéder aux ressources NovaTech est **autorisée uniquement** pour la messagerie professionnelle (Gmail NovaTech via navigateur) et Slack (app mobile). L'accès VPN depuis un appareil personnel est **interdit** sauf autorisation écrite du RSSI.

---

## 4. Télétravail et accès distant

### 4.1 VPN obligatoire

L'accès à tout système interne NovaTech (hors Gmail et Slack) depuis l'extérieur des locaux **nécessite obligatoirement** l'activation du VPN **NordLayer**. Le client NordLayer est pré-installé sur tous les appareils NovaTech.

**Serveurs VPN recommandés :** Paris-FR-01 (le plus proche, latence minimale) ou Amsterdam-NL-01 (fallback).

### 4.2 Réseaux Wi-Fi en télétravail

- Réseau domestique personnel : autorisé avec VPN actif
- Wi-Fi public (café, coworking, hôtel) : **interdit sans VPN**. Avec VPN actif : toléré pour les usages non sensibles uniquement
- Réseau 4G/5G partage de connexion mobile : autorisé

### 4.3 Règles spécifiques pour les données sensibles

Toute manipulation de données clients, contrats, données financières ou données personnelles (RGPD) depuis un lieu de télétravail doit se faire :
- Sur l'équipement NovaTech (jamais sur appareil personnel)
- Via VPN actif
- Dans un espace garantissant la confidentialité visuelle (pas en open space de coworking public)

---

## 5. Gestion des données et confidentialité (RGPD)

### 5.1 Classification des données

| Niveau | Description | Exemples | Stockage autorisé |
|--------|-------------|---------|-------------------|
| PUBLIC | Informations diffusables librement | Site web, communiqués | Tout support |
| INTERNE | Usage collaborateurs uniquement | Cette documentation | Drive NovaTech, SharePoint |
| CONFIDENTIEL | Accès restreint, besoin identifié | Contrats clients, données RH | Drive NovaTech chiffré, SharePoint privé |
| SECRET | Très haute sensibilité | Code source propriétaire, levée de fonds | GitHub privé, partage individuel |

### 5.2 Durées de conservation

- Données salariés : 5 ans après fin du contrat (obligations légales URSSAF)
- Contrats clients : 10 ans après fin de la relation contractuelle
- Données prospects (CRM) : 3 ans après dernier contact
- Logs de connexion système : 12 mois

### 5.3 Violation de données — obligation de signalement

Toute violation (ou suspicion de violation) de données personnelles doit être signalée au **DPO (dpo@novatech.io)** dans les **24 heures** suivant la découverte. Le DPO dispose de **72 heures** pour notifier la CNIL si nécessaire (art. 33 RGPD).

---

## 6. Incidents de sécurité — procédure de signalement

### Étapes à suivre impérativement

1. **Ne pas éteindre ni déconnecter** le poste compromis (préservation des preuves)
2. **Appeler immédiatement** l'astreinte sécurité : **+33 6 44 55 66 77** (24h/24, 7j/7)
3. **Envoyer un email** à security@novatech.io avec : description de l'incident, heure de découverte, systèmes potentiellement affectés
4. **Ne pas communiquer** sur l'incident en dehors du canal sécurité (pas de Slack, pas d'email interne)

### Types d'incidents à signaler

- Phishing reçu ou cliqué (même si vous n'avez pas saisi d'identifiants)
- Perte ou vol d'un équipement NovaTech
- Accès inhabituel à votre compte (alerte MFA non initiée par vous)
- Ransomware ou comportement suspect du poste
- Partage accidentel de données confidentielles à l'externe

---

## 7. Outils autorisés et interdits

### ✅ Outils approuvés par la DSI

| Catégorie | Outil autorisé |
|-----------|---------------|
| Messagerie | Gmail (@novatech.io) |
| Communication | Slack (espace NovaTech uniquement) |
| Vidéoconférence | Google Meet |
| Gestion de code | GitHub (org NovaTech), GitLab auto-hébergé |
| Documentation | Notion (espace NovaTech) |
| Stockage cloud | Google Drive (compte NovaTech), SharePoint NovaTech |
| Gestion de projet | Linear |
| RH | Factorial |
| Gestionnaire de mots de passe | 1Password (licence entreprise) |
| VPN | NordLayer |
| Monitoring | Datadog, Sentry |

### ❌ Outils interdits (sans autorisation écrite DSI)

- Dropbox, WeTransfer, OneDrive personnel, iCloud
- ChatGPT, Claude.ai, Gemini (version grand public) pour données confidentielles
- WhatsApp, Telegram, Signal pour échanges professionnels sensibles
- Logiciels de prise de contrôle à distance non autorisés (TeamViewer perso, AnyDesk)

> **Note IA** : L'utilisation d'outils IA générative est encadrée par la **Politique IA NovaTech (DSI-IA-POL-2025-v1)**. Des accès sécurisés à des API IA sont disponibles pour les projets autorisés — contacter la DSI.

---

## 8. Formations obligatoires

| Formation | Fréquence | Plateforme | Durée |
|-----------|-----------|-----------|-------|
| Sensibilisation cybersécurité (base) | À l'onboarding | Didask | 2h |
| Phishing simulation | Trimestrielle | KnowBe4 | ~10 min |
| RGPD & Protection des données | Annuelle | Didask | 1h30 |
| Gestion des incidents de sécurité | Annuelle | Présentiel ou visio | 1h |

La non-completion des formations obligatoires dans les délais impartis est signalée au manager et à la DRH.

---

## 9. Sanctions et responsabilités

Le non-respect des présentes règles est susceptible d'entraîner des sanctions disciplinaires conformément au Règlement Intérieur NovaTech (RH-RI-v2.1, Article 4) et peut, selon la gravité, constituer une faute grave ou lourde justifiant un licenciement sans préavis ni indemnité.

En cas de dommages causés volontairement ou par négligence grave, la responsabilité civile et pénale du collaborateur peut être engagée.

---

_Document : DSI-SEC-2025-v3 | RSSI : Luca Ferrari — l.ferrari@novatech.io_
_Astreinte sécurité 24/7 : +33 6 44 55 66 77 | security@novatech.io_
_Prochaine révision : janvier 2026_
