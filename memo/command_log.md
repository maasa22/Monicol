// create a GitHub repositorie named "Monicol" on Chrome // choose all of the default settings (no readme, no gitignore, no licence)

// execute an first commit, following directions on https://github.com/maasa22/Monicol
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/maasa22/EssayShares.git
git push -u origin main

// create a nuxt project // choose all of the default settings except vuetify. details are below
yarn create nuxt-app client

// see client locally
cd client
yarn install
yarn dev // acccess http://localhost:3000/

// set up firebase // refrence: https://github.com/firebase/functions-samples/tree/master/stripe
// create a project at firebase console named "Monicol-service" on Chrome
// Enable billing on your project by switching to the Blaze plan.
firebase login
start firestore on firebase console // choose test mode
Enable Google & Email sign-in on firebase console
firebase init
// check firestore, functions, hosting
// In other parts, check default settings

// dev server locally
firebase serve --only functions

// dev client locally
cd client
yarn install
yarn dev

// deploy server
firebase deploy --only functions

// deploy client
cd client
yarn generate // perhaps "firebase serve --only hosting" is also ok
firebase deploy -- only hosting // change deploy directory in firebase.json

// set up firestore for client
yarn add firebase
// access firebase console > プロジェクトの設定 > マイアプリ > ウェブアプリに Firebase を追加
// create plugins/firebase.js // https://qiita.com/ririli/items/d0d3a6ae78c1b6e827fc

// set up stripe
yarn add nuxt-stripe-module

// set up firebaseui
yarn add firebaseui

// set up stripe
firebase functions:config:set stripe.secret=<YOUR STRIPE SECRET KEY>

// import server dependencies
cd functions
yarn add @google-cloud/logging
yarn add stripe

// have access from python
// firebase console > プロジェクトの設定 > サービスアカウント > 新しい秘密鍵の生成
pipenv shell
pipenv install firebase_admin
pipenv install

# detail logs

## nuxt project config

? Project name: client
? Programming language: JavaScript
? Package manager: Yarn
? UI framework: (Use arrow keys)
? UI framework: Vuetify.js
? Nuxt.js modules: (Press <space> to select, <a> to toggle all, <i> to invert selection)
? Linting tools: (Press <space> to select, <a> to toggle all, <i> to invert selection)
? Testing framework: None
? Rendering mode: Universal (SSR / SSG)
? Deployment target: Server (Node.js hosting)
? Development tools: (Press <space> to select, <a> to toggle all, <i> to invert selection)
? What is your GitHub username? masaki
? Version control system: Git

## firebase config

? Which Firebase CLI features do you want to set up for this folder? : check firestore, functions, hosting
? Please select an option: Use an existing project
? Select a default Firebase project for this directory: monicol-service (Monicol-service)
? What file should be used for Firestore Rules? firestore.rules
? What file should be used for Firestore indexes? firestore.indexes.json
? What language would you like to use to write Cloud Functions? JavaScript
? Do you want to use ESLint to catch probable bugs and enforce style? No
? Do you want to install dependencies with npm now? Yes
? What do you want to use as your public directory? public
? Configure as a single-page app (rewrite all urls to /index.html)? No
? Set up automatic builds and deploys with GitHub? No
