# Guide d'Utilisation - B2P.AI

## Problèmes Résolus

### 1. ✅ Les tâches créées s'affichent maintenant immédiatement

**Problème** : Lorsque vous créiez une tâche, elle ne s'affichait pas dans votre liste.

**Solution** : Le champ `assigned_to` est maintenant automatiquement défini lors de la création d'une tâche.

**Comment utiliser** :
1. Allez sur la page "Task Management"
2. Cliquez sur le bouton "New Task"
3. Remplissez les informations :
   - Titre (obligatoire)
   - Description
   - Niveau d'urgence (1-5)
   - Effort estimé (en heures)
4. Cliquez sur "Create Task"
5. ✨ La tâche apparaît immédiatement dans votre liste !

**Fichier modifié** : [frontend/src/pages/TaskManagement.tsx:116](frontend/src/pages/TaskManagement.tsx#L116)

---

### 2. ✅ Page Team - Affichage des membres de l'équipe en temps réel

**Problème** : La page Team affichait des données fictives.

**Solution** : La page Team se connecte maintenant au backend pour afficher les vraies données de votre équipe.

**Informations affichées** :
- **Nom et rôle** de chaque membre
- **Tâches actives** (pending + in_progress)
- **Tâches complétées cette semaine**
- **Score de charge de travail** (somme des efforts estimés)
- **Risque de burnout** (de 0% à 100%)
- **Productivité** calculée automatiquement

**Comment utiliser** :
1. Allez sur la page "Team View"
2. Si vous n'êtes pas dans une équipe, un message d'erreur s'affiche
3. Si vous êtes dans une équipe, vous voyez :
   - **Statistiques globales** : Taille de l'équipe, tâches actives, tâches complétées, risque moyen de burnout
   - **Cartes des membres** : Vue détaillée de chaque membre avec leurs métriques
   - **Tableau détaillé** : Analyse de distribution de la charge de travail
4. Cliquez sur "Actualiser" pour rafraîchir les données

**Fichier modifié** : [frontend/src/pages/TeamView.tsx](frontend/src/pages/TeamView.tsx)

---

### 3. ✅ Auto-refresh pour les tâches reçues par email

**Problème** : Les tâches reçues par email n'apparaissaient pas automatiquement.

**Solution** : La page Task Management se rafraîchit automatiquement toutes les 30 secondes.

**Comment ça marche** :
1. Le système backend surveille votre boîte email
2. Quand un email avec une tâche arrive :
   - Le système extrait les informations (titre, description, urgence, deadline)
   - La tâche est automatiquement créée et assignée en fonction de votre email
   - Source = "email"
3. Dans les 30 secondes, la tâche apparaît dans votre liste de tâches !

**Indicateur visuel** :
- Les tâches créées manuellement ont `source: "manual"`
- Les tâches reçues par email ont `source: "email"`

**Pour tester** :
1. Envoyez un email à l'adresse configurée dans le système
2. Attendez maximum 30 secondes
3. La tâche apparaît automatiquement dans votre liste !

**Fichier modifié** : [frontend/src/pages/TaskManagement.tsx:64-73](frontend/src/pages/TaskManagement.tsx#L64-L73)

---

## Flux Complet d'Utilisation

### Scénario 1 : Créer une tâche manuellement

1. **Login** sur http://localhost:3000/login
   - Email : alice.martin@b2p.ai
   - Password : (votre mot de passe)

2. **Navigation** vers Task Management

3. **Création** d'une tâche :
   - Cliquez sur "New Task"
   - Titre : "Implémenter la nouvelle fonctionnalité X"
   - Description : "Ajouter la fonctionnalité X"
   - Urgence : 4
   - Effort : 8 heures
   - Cliquez "Create Task"

4. **Résultat** : La tâche apparaît immédiatement dans votre liste

### Scénario 2 : Recevoir une tâche par email

1. **Email reçu** avec une tâche
2. **Système backend** :
   - Détecte l'email (vérification toutes les 60 sec)
   - Extrait les informations de la tâche
   - Crée automatiquement la tâche
   - Assigne à l'utilisateur basé sur l'email

3. **Frontend** :
   - Auto-refresh toutes les 30 secondes
   - La tâche apparaît automatiquement
   - Source = "email"

### Scénario 3 : Voir votre équipe

1. **Allez sur Team View**
2. **Visualisez** :
   - Statistiques globales de l'équipe
   - Cartes des membres avec leurs métriques
   - Tableau détaillé de distribution
3. **Cliquez "Actualiser"** pour rafraîchir les données

---

## FAQ

### Q1 : Pourquoi mes tâches créées ne s'affichent pas ?

**R** : Ce problème est maintenant résolu ! Les tâches sont automatiquement assignées à vous lors de la création. Si vous ne les voyez toujours pas :
- Rafraîchissez la page
- Vérifiez que vous êtes connecté
- Vérifiez les logs du backend

### Q2 : Comment voir mon équipe ?

**R** : Vous devez avoir un `team_id` assigné. Vérifiez avec :
```sql
SELECT id, name, email, team_id FROM employees WHERE email = 'votre-email';
```

Si `team_id` est NULL, assignez-en un :
```sql
UPDATE employees SET team_id = 'id-de-votre-team' WHERE email = 'votre-email';
```

### Q3 : Les tâches email apparaissent-elles automatiquement ?

**R** : Oui ! Le système vérifie automatiquement :
- Backend vérifie emails : toutes les 60 secondes
- Frontend rafraîchit liste : toutes les 30 secondes
- Délai maximum : ~90 secondes

### Q4 : Puis-je désactiver l'auto-refresh ?

**R** : Oui, commentez ces lignes dans TaskManagement.tsx (lignes 64-73) :
```javascript
/*
useEffect(() => {
  const intervalId = setInterval(() => {
    if (token && user && !loading) {
      fetchTasks();
    }
  }, 30000);
  return () => clearInterval(intervalId);
}, [token, user, loading]);
*/
```

---

## Configuration Email (Pour l'Auto-Assignment)

### Fichier `.env` du Backend

```env
# Configuration Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

# IMAP pour lire les emails
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
```

### Pour Gmail

1. Activez l'authentification à 2 facteurs
2. Créez un "Mot de passe d'application"
3. Utilisez ce mot de passe dans `EMAIL_PASSWORD`

### Démarrer le Worker Email

```bash
cd backend
python -m app.workers.email_worker
```

---

## Dépannage

### Erreur : "You must be part of a team"

**Solution** : Assignez un team_id à votre utilisateur (voir Q2 ci-dessus)

### Erreur : "Failed to load tasks"

**Solutions** :
1. Vérifiez que le backend tourne : http://localhost:8000/docs
2. Déconnectez-vous et reconnectez-vous
3. Vérifiez les logs backend

### Erreur : "Failed to load team data"

**Solutions** :
1. Vérifiez votre team_id
2. Exécutez le seed script : `python scripts/seed_data.py`
3. Vérifiez que l'endpoint `/teams/{team_id}/members` fonctionne

---

## Résumé des Corrections

| Problème | Solution | Statut |
|----------|----------|--------|
| ❌ Tâches créées non visibles | ✅ Ajout automatique de `assigned_to` | Résolu |
| ❌ Page Team avec données mockées | ✅ Connexion au backend API | Résolu |
| ❌ Tâches email non affichées auto | ✅ Auto-refresh toutes les 30 sec | Résolu |

**Toutes les fonctionnalités sont maintenant opérationnelles !** 🎉
