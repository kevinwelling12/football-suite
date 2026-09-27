# Setup: Firebase sync + GitHub Pages hosting (about 20 minutes, all free)

The code is done. These are the one-time account steps only you can do.

## 1. Firebase project
1. Go to https://console.firebase.google.com, sign in with your Google account, **Create a project**
   (e.g. "football-suite"). Google Analytics: off. Plan: Spark (free) is the default.
2. **Build > Authentication > Get started > Sign-in method > Google > Enable**, pick your support
   email, Save.
3. **Build > Firestore Database > Create database**. Location: `us-west2 (Los Angeles)` (closest to
   Sacramento; can't be changed later). Start in **production mode**.
4. Firestore > **Rules** tab: replace everything with the contents of `firestore.rules` from this
   repo, **Publish**.
5. **Project settings (gear) > General > Your apps > Web (</>)**. Nickname "web", no Hosting
   checkbox, Register. Copy the `firebaseConfig` object it shows.
6. Paste it into `src/firebase-config.js` as `window.FIREBASE_CONFIG = { ... };`. These values are not
   secret (the rules protect your data), so it's fine to commit them.

## 2. GitHub Pages
1. Create a GitHub repo (public is simplest for free Pages; private repos need a paid plan for Pages)
   and push this folder to the `main` branch.
2. Repo **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. Every push to `main` builds (`scripts/build.py`) and deploys `dist/web`. The site will be at
   `https://<your-username>.github.io/<repo-name>/`.
   Note: a public repo also publishes `user-data/` (your entered scores, follows, settings). If you'd
   rather not, delete `user-data/` after your first successful sign-in (the data is in Firestore by then).

## 3. Allow the site to sign in
Firebase console > **Authentication > Settings > Authorized domains > Add domain**:
`<your-username>.github.io`

## 4. First run
1. Open the site in Safari on your iPhone, tap **Sign in to sync** (in the header or Settings > Your
   data) and pick your Google account.
2. First sign-in with an empty cloud: the app loads your exported data from `user-data/` (bundled at
   build time) and uploads it. Your results, follows, postponement, reschedule, settings and Match of
   the week locks all carry over.
3. Sign in on the iPad too. From then on, changes on one device appear on the other within seconds;
   offline changes sync when you're back online.
4. Home screen: Safari > Share > **Add to Home Screen**. (It opens in Safari, which keeps Google sign-in
   reliable.)

## Troubleshooting
- "auth/unauthorized-domain": step 3 not done or typo in the domain.
- Sign-in popup blocked: allow popups for the site, or the app falls back to a redirect sign-in.
- Nothing syncs: check Firestore Rules were published and that both devices show "Synced to <email>".
