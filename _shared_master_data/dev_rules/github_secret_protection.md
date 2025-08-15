# GitHub 秘密情報流出防止ルール
1) コミット前: 実キーは .env に置き、.env は gitignore。 .env.example はプレースホルダのみ。
2) .gitignore: .env / .env.local / *.env / *.key / *.token を除外。
3) 自動検知: detect-secrets の .secrets.baseline を維持。pre-push で差分検知しブロック。
4) 事故時復旧: 
   git-filter-repo --force --invert-paths --path .env --path .env.example
   git push --force
