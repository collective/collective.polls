---
myst:
  html_meta:
    "description": "Run your first poll with collective.polls: create it, open it, vote, show it on a page, and close it."
    "property=og:description": "Run your first poll with collective.polls: create it, open it, vote, show it on a page, and close it."
    "property=og:title": "Run your first poll"
    "keywords": "Plone, Volto, polls, tutorial, vote, Poll block"
---

# Run your first poll

In this tutorial you run a poll from start to finish.
You create it, open it to visitors, vote in it as an anonymous visitor, show it on the home page, and close it to publish its final results.

It takes about fifteen minutes.

## Before you start

You need a site with both add-ons installed.
The quickest way is the development environment in this repository, which comes with example content.
Follow {doc}`/how-to-guides/install/development`, then keep both servers running.

You log in as the `admin` user, with the password `admin`.

## Create a folder for your polls

Anonymous visitors can only vote in a poll they can see, and a poll inherits its visibility from its folder.
So the poll goes into a published folder.

1.  Open http://localhost:3000/ and log in.
2.  Add a **Page** at the root of the site, titled `Polls`, and save it.
3.  From the page's **State** menu in the toolbar, choose **Publish**.

## Create the poll

1.  Inside the `Polls` page, add a **Poll**.
2.  Set the **Title** to `Which fruit do you like best?`.
3.  Open the **Voting** fieldset.
    -   Keep **Allow anonymous** checked.
    -   Keep **Number of options a voter can pick** at `1`.
    -   Under **Available options**, add three options: `Apple`, `Banana`, and `Cherry`.
4.  Open the **Results** fieldset.
    -   Keep **Show partial results** checked.
    -   Set **Graph** to **Pie Chart**.
5.  Save the poll.

The poll is now *Private*: only you and other editors can see it, and nobody can vote yet.
The poll view shows its options without a vote button.

## Open the poll

From the poll's **State** menu, choose **Open**.

As an administrator, you can open a poll directly.
A contributor without the reviewer role would choose **Submit for opening** instead, and a reviewer would open it.

The poll now shows a vote button.
As you are logged in, you could vote right away as `admin`, but this tutorial votes as a visitor instead.

## Vote as an anonymous visitor

1.  Open a private browser window, and go to http://localhost:3000/polls/which-fruit-do-you-like-best.
2.  Pick **Cherry**, and choose **Vote**.

The poll says **Thanks for your vote**, and shows the partial results as a pie chart.
Reload the page: the poll remembers that you voted, from a cookie it set, and keeps showing the results instead of the form.

## Show the poll on the home page

1.  Back in your logged-in window, edit the home page.
2.  Add a **Poll** block.
3.  In the block's settings, keep **Which poll** at **Latest opened poll**, and set **Header** to `Today's poll`.
4.  Save the page.

The block shows the newest open poll of the site, which is yours.
When you open another poll later, the block shows that one instead, without editing the page again.

## Close the poll

From the poll's **State** menu, choose **Close**.

A closed poll accepts no more votes, and everyone sees its final results, including visitors who never voted.
In the private window, reload the poll: it says **This poll is closed.**, and the results are no longer headed **Partial results**.

The Poll block on the home page shows nothing now, because no poll is open.
To keep showing the latest results there, edit the block and check **Show closed polls**.

## What you learned

-   A poll collects votes only while it is *Open*, and only from people who can see it.
-   Anonymous voting needs a published folder before the poll is opened.
-   The Poll block follows the newest open poll, or shows a poll you pick.
-   Closing a poll publishes its results to everyone.

Next, read {doc}`/concepts/voting-and-results` to understand who can vote and how votes are counted, or {doc}`/reference/content-type` for every setting of a poll.
