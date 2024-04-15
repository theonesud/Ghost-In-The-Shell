# User stories

user signs up for wishlist
user wishlist gets approved and gets a signup link in email

user creates an account
user logs in
user will connect CC to it
user will connect online accounts to it

user sees a list of bots
user can use an existing bot
user will configure the bot
user runs the bot manually
user sees the logs of the bot
user gets notified by email daily with logs of the bot

user can create a bot

# Bots

## IO pieces (with user's personal data)

-   shopify

-   zapier

-   google sheet
-   google doc
-   gmail

-   aws ec2
-   postgresql

-   youtube

-   github

-   api

-   whatsapp
-   fb
-   insta
-   twitter
-   slack

-   csv
-   json
-   pandas df

## Internals (with global data)

-   wikipedia
-   wolframalpha
-   gpt
-   google search
-   generate image
-   metaprompt
-   data analysis
-   step by step problem breaker
-   compare multiple outputs
-   question asker
-   download urls
-   KeywordExtractor
-   LanguageTranslator
-   GrammarCorrector
-   LanguageImprover
-   Synonym
-   Antonym
-   Etymologist
-   SentimentAnalyser
-   Summary
-   Simplify
-   human
-   shell
-   python repl
-   fileops

## Usecases

18. talk to a regional customer support representative - bot9

-   Input: real time input
-   Configure: GPT to give the right response
-   Output: real time output, API endpoint returning the resp

17. sales agent linkedin scraper to get emails -

-   research companies from a location and revenue (from crunchbase) - mvp (we'll give company names)
-   search company's linkedin, find decision maker's people, dm and email (hunter.io, easyleads)

0. ai job board

-

1. search shopify catalog - uses chat based search to find the product in the catalog. (set and forget - Will be used by 3rd person)

-   Input: shopify, real time input
-   Config: GPT to write the right filtering query
-   Run shopify query
-   Output: real time output, API endpoint returning the filtered products

2. talk to a business analyst - runs analysis on your sales data to answer any business questions

-   google ads, livedocs integrations,
-   Input: Sheets, postgresql, real time input
-   Config: GPT to write the right pandas code, sql query
-   Run pandas code / sql
-   Output: real time output, API

17. shopify tag generator
18. shopify desc generator

19. job interviewer prep

20. email replier

-   Input: gmail
-   configure: which emails to reply to
-   gpt to provide the right response
-   output: gmail, API

5. twitter replier

-   Input: twitter
-   configure: which tweets to reply to
-   gpt to provide the right response
-   output: twitter, API

6. code writer

-   input: github, realtime input
-   configure: template files
-   output: github

7. prd writer, project manager, backendengineer, fe

-   input: notion/googledocs, realtime input
-   configure gpt
-   output: notion/googledocs, realtime output

8. code translator

-   input: github, realtime input
-   configure: languages, packages on both sides
-   output: github

9. code documenter

-   input: github, realtime input
-   configure: gpt
-   output: github

10. code reviewer

-   input: github, realtime input
-   configure: gpt TimeComplexity, BugFinder, CodeImprover
-   output: github

11. twitter creator

-   input: twitter, realtime input
-   configure: gpt
-   output: twitter

12. blogger

-   input: notion/googledocs, realtime input
-   configure: gpt
-   output: notion

13. find topics to write about

-   input: twitter, medium, specific websites

15. InteractiveFiction

16. AsciiArtist
