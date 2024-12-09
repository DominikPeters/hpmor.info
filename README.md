# hpmor.info
An Annotated Version of Harry Potter and the Methods of Rationality

This is the source of the website [hpmor.info](https://hpmor.info) which contains the text of Eliezer Yudkowsky's Harry Potter fanfiction [Harry Potter and the Methods of Rationality](http://www.hpmor.com) with annotations explaining foreshadowing and other details. Many of the annotations are taken from comments in the [/r/HPMOR subreddit](https://www.reddit.com/r/HPMOR/).

## Contributing

Contributions of notes are welcome! Please open a pull request with your changes. A convenient way to contribute is to use the `github.dev` interface. Paragraphs on hpmor.info have a <kbd>+</kbd> link to their left, which opens a VS Code editor in your browser with the corresponding file open and the paragraph selected. You can then make your changes and open a pull request directly from the editor.

The notes are stored in yaml files in the `yaml` directory. Each chapter has its own file named `<number>.yaml`. The format is as follows:

```yaml
131:
  text: |-
    "I don't sleep right," Harry said. He waved his hands helplessly. "My sleep
    cycle is twenty-six hours long, I always go to sleep two hours later, every day.
    I can't fall asleep any earlier than that, and then the next day I go to sleep
    two hours later than <em>that.</em> 10PM, 12AM, 2AM, 4AM, until it goes around
    the clock. Even if I try to wake up early, it makes no difference and I'm a
    wreck that whole day. That's why I haven't been going to a normal school up
    until now."
  notes:
  - type: original
    date: 2020/04/30
    author: hpmor.info
    text: |
      <p>
        Harry's sleep cycle is 2 hours too long because Dumbledore slipped him a
        potion in order to fulfil a prophecy.
        <a class="link-hpmor" href="https://hpmor.info/chapter/119/#19126">Chapter 119</a>
      </p>
```
The date should refer to the date that the note was written. The author is optional. The text should use HTML, typically a single `<p>`-wrapped paragraph.

The link in the example goes to a specific paragraph. You can find links to paragraphs on hpmor.info by checking the gray "anchor" links to the left of each paragraph. Use `class="link-hpmor"` for links to hpmor.info and `class="link-reddit"` for links to Reddit, and no class for links to other sites.

Normal notes should have `- type: original`. There are also `- type: reddit` notes which are taken from Reddit comments. These should have a `comment` field with the comment ID. For example:

```yaml
1424:
  text: |-
    "Just kidding! RAVENCLAW!"
  notes:
  - type: reddit
    author: EliezerYudkowsky
    url: https://reddit.com/r/HPMOR/comments/4h2t8c/the_incident_with_the_sorting_hat_spoilers_all/d3312wg/
    date: 2016/05/12
    score: 8
    text: |
      <p>
        It was either the Sorting Hat or Dumbledore. Professor Quirrell would have
        left him in Slytherin, <em>of course</em>.
      </p>
```

It may be useful to support similar syntax for other types of notes in the future, such as LessWrong comments. Feel free to implement this if you want to, or open an issue if you want me to look into it.