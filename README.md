# 4RealBot - Bot Discord multifonction

Un bot Discord en Python avec plusieurs fonctionnalités utiles : modération, jeux, interaction avec OpenAI, gestion d'annonces, sondages, et plus encore.

---

## Fonctionnalités

- ⚠️ **Warn**: avertir un membre, avec système de bannissement automatique après 3 warns  
- 🎲 **Jeu Pierre-Papier-Ciseaux**  
- 💬 **Ask** : poser une question à ChatGPT via OpenAI  
- 📅 **Rappel automatique** toutes les heures (modifiable)  
- 📢 **Annonce** : envoyer une annonce dans un canal configuré  
- 🎉 **Giveaway** : lancer un tirage au sort  
- 📊 **Poll** : créer un sondage simple  
- 🎫 **Ticket** : système de ticket de support  
- 🔍 **Userinfo** : afficher les infos d’un membre  
- 💬 **Quote** : envoyer une citation aléatoire  

---

## Installation

1. Clone ce dépôt :

   ```bash
   git clone https://github.com/Kg4REAL/4RealBot.git 
   cd 4RealBot

2. Crée un environnement virtuel:

python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

3. Installe les dépendances :
pip install -r requirements.txt

4. Crée un fichier .env à la racine du projet avec tes clés d’API
DISCORD_TOKEN=ton_token_discord_ici
OPENAI_API_KEY=ta_cle_openai_ici

Usage
Lance le bot avec la commande :
python bot.py

## Configuration
Certaines commandes nécessitent que tu configures des channels (exemple : annonces, support tickets). Utilise la commande /config pour les définir.

## Contribution
N’hésite pas à proposer des améliorations via pull requests ou issues !

## Licence
Code open-source – libre d’utilisation à but éducatif.

## Contact
Pour toute question, contacte-moi sur Discord : kg_4real

