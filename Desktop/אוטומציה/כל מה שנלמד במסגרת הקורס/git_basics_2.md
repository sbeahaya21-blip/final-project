# Git Branching

Branching means you diverge from the main line of development and continue to do work without messing with that main line.

A **branch** in Git is simply a lightweight movable pointer to consecutive commits. 
The default branch name in Git is `master` (or `main` if the repo was initially created in GitHub). 
As you start making commits, you're given a `main` branch that points to the last commit you made.
Every time you commit, the `main` branch pointer moves forward automatically.

## Creating a new branch and check them out

You can create a new branch using the `git branch` command:

```bash 
git branch testing
```

What happens when you create a new branch? Well, doing so creates a new pointer for you to move around.
How does Git know what branch you're currently on? It keeps a special pointer called `HEAD`. `HEAD` is a pointer to the local branch you're currently on.

To switch to an existing branch, you run the `git checkout` command. 

```bash
git checkout testing
```

> [!TIP]
> You can create the branch and check it out as well at the same command:
> 
> ```bash
> git checkout -b testing
> ```

Your testing branch has moved forward, but your `main` branch still points to the commit you were on when you ran git checkout to switch branches. Let's switch back to the main branch:

```bash
git checkout main
```

That command did two things. It moved the `HEAD` pointer back to point to the `main` branch, and it reverted the files in your working directory back to the snapshot that main points to.

Let's make a few changes (on branch `main`) and commit again. Visualize. 

## Merging branches

1. Checkout branch main: `git checkout main`.
2. Let's create a new branch which represents some feature we are going to work on: `git checkout -b myfeature1`.
3. Commit some changes in `myfeature1`.

Now we want to merge `myfeature1` into `main`.
Merging branches basically combines the changes from one branch into another. 

**In order to merge one branch into another, you need to checkout the branch that you want to merge into.** 

7. Since we want to merge `myfeature1` into `main`: `git checkout main`.
8. Then merge by: `git merge myfeature1`. This command merges `myfeature1` into `main`. 

## Merge conflicts 

Occasionally, this process of merging doesn't go smoothly. 
If you changed the same part of the same file differently in the two branches you're merging, Git won't be able to merge them cleanly.

Let's simulate this scenario. 

1. Checkout branch `main`.
2. Create the following commits structure, as detailed below:   
   ![][git_merge_conflict]
   1. In branch `main` create a file called `file1` and commit it. 
   2. Check out a new branch called `dev`. In that branch create a file called `file2` with the below content and commit it:
      ```text
      Apple
      Banana
      Orange
      ```
   3. Checkout branch `main`, create a file called `file2` too, with the below content and commit it:
      ```text
      Apple
      Pear
      Orange
      ```
   4. This why the two commits are conflicted. 
   5. Create `file3` and commit it.
3. Now merge **`main` into `dev`**!

Git hasn't automatically created a new merge commit.
It has paused the process while ask you to resolve the conflict. 
If you want to see which files are unmerged at any point after a merge conflict, you can run `git status`. 

**Git stages all unconflicted files, while moves conflicted files to the working tree:** 

![][git_merge_conflict2]

Git adds standard conflict-resolution markers to the files that have conflicts, so you can open them manually and resolve those conflicts.

Your `file2` contains a section that looks something like this:

```text
<<<<<<< HEAD:file2
Banana
=======
Pear
>>>>>>> main:file2
```

In order to resolve the conflict, you have to either choose one side or the other or merge the contents yourself.

4. After you've chosen the correct version, run `git add`. Staging the file marks it as resolved in Git.
5. Commit the change.


## Pull Requests 

In real-life projects, the `main` branch usually represents **production code** — code that is running (or is ready to run) in production.
Because of that, **you should not merge directly into `main` from your local machine**.

Instead, the correct and safe way to get your work into `main` is by using a Pull Request (PR).

A Pull Request is a request to merge one branch (for example, `myfeature1`) into another branch (usually `main`) via the remote repository (e.g. GitHub).
It allows others to:

- Review your code by other team members
- Run automated tests and checks (CI)
- Discuss changes before they reach production

# Exercises 

### :pencil2: Git workflow and Pull Requests

**Git workflow** is a set of practices that developers follow when working with Git to manage their codebase effectively.

In this exercise we will practice the Git workflow that will be used throughout this course.

Let's say you are tasked to implement a change to the `POST /extract` endpoint, 
in which you need to **measure the time** it takes to get a prediction from the OCI Document Understanding service.

How do you work with Git to implement this change?

1. From branch `main`, create a new branch for your task:
   ```bash
   git checkout -b extract_pediction_time
   ```
2. Implement the code changes in `app.py`:

   ```python
   @app.post("/extract")
   async def extract(file: UploadFile = File(...)):
       ...
       
       response = doc_client.analyze_document(request)   ####### This is the line that makes the prediction call, use time.time() to measure the time it takes to get the response #######
       
       ...
   
       result = {
        "confidence": "1",
        "data": data,
        "dataConfidence": data_confidence
        "predictionTime": prediction_time  # add the prediction time to the response
       }
   ```

3. Commit & push your changes.
4. Create a pull request (PR) in GitHub from your branch `extract_pediction_time` to `main`.
   Let the PR pass the Continues Integration (CI) checks and get approved by a reviewer.
5. Merge the PR it into `main`. 
6. Well done! You have successfully implemented a new feature and tested it.




[git_branch5]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_branch5.png
[git_branch6]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_branch6.png
[git_merge_conflict]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_merge_conflict.png
[git_merge_conflict2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_merge_conflict2.png
[git_rebase1]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_rebase1.png
[git_rebase2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_rebase2.png
[git_rebase3]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_rebase3.png
[git_rebase4]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_rebase4.png