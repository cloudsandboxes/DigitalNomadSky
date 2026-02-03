Welcome to NomadSky docs contributing guide
Thank you for investing your time in contributing to our project! Any contribution you make will be reflected ✨.

📖 This is our canonical source for all contribution processes and policies.

Read our Code of Conduct to keep our community approachable and respectable.

This guide provides repository-specific information to supplement the official contribution documentation.

Use the table of contents icon Table of contents icon in the top corner of this document to get to a specific section of this guide quickly.

New contributor guide

For repository-specific setup, read the README file. The official docs site also provides these helpful resources:

Finding ways to contribute to open source on GitHub
Set up Git
GitHub flow
Collaborating with pull requests
Contribution types and what we're looking for
Content we accept:

Technical and grammatical corrections
Typo fixes
Expanded explanations of existing products or features, when the expansion has a compelling reason
New content filling important gaps in our documentation. For example, this pull request added a useful section on security hardening for GitHub Actions.
Content we do not currently accept:

Edits purely for tone, readability, or efficiency
Topics that are too niche or a matter of personal preference
Changes to the underlying site and workflows
These are general guidelines, but if you’re not sure what category your proposed change would fall under, feel free to open an issue to discuss it with us!

Getting started

For repository-specific information:

See the introduction to working in the docs repository 🎊
Check our types of contributions we accept
Review our markdown style guidelines in the /contributing directory
Writing style guidelines
When contributing content, please follow these key principles from our style guide:

Clarity and simplicity: The goal of our writing style is clarity and simplicity.
Meaning over grammar: Grammatical correctness is important, but not as important as clarity and meaning.
Second person: The docs use second-person ("you") to communicate directly with readers.
Inclusive language: Use inclusive language by not assuming gender or ability level, and by avoiding slang and idioms.
Accessible technical language: Jargon is sometimes necessary, but don't assume every reader has your technical expertise.
Active voice: Use active voice wherever possible. Active voice means avoiding "be" verbs like "is" or "are" when you can, but also choosing more dynamic verbs to get your point across. "Press (a key)" is less dynamic than "tap (a key)," for example.
Clear terminology: Avoid technical abbreviations like "repo" and "PR," and Latin abbreviations like "i.e." and "e.g."
For complete style guidance, see our style guide.

Repository-specific notes:
Search existing issues before creating new ones
Use our label reference to categorize appropriately
Follow the issue templates provided in this repository
Make Changes

Repository-specific options:
Make changes in the UI: Click Make a contribution at the bottom of any docs page for small changes like typos or broken links.

Make changes in a codespace: See "Working in a codespace" for documentation-specific setup.

Make changes locally:

Fork the repository (see official forking guide)
Install Node.js at the version specified in .node-version (see development guide)
Create a working branch and start with your changes
Commit your update

Use our "Self review checklist" before committing.

Pull Request

Repository-specific notes:

Fill the "Ready for review" template
Link PR to issue if applicable
Enable maintainer edits
A Docs team member will review following our standard review process.

Your PR is merged!
Congratulations 🎉🎉
Once merged, your contributions will be visible.

Continue contributing using our types of contributions.

Windows
This site can be developed on Windows, however a few potential gotchas need to be kept in mind:

Regular Expressions: Windows uses \r\n for line endings, while Unix-based systems use \n. Therefore, when working on Regular Expressions, use \r?\n instead of \n in order to support both environments. The Node.js os.EOL property can be used to get an OS-specific end-of-line marker.
Paths: Windows systems use \ for the path separator, which would be returned by path.join and others. You could use path.posix, path.posix.join etc and the slash module, if you need forward slashes - like for constructing URLs - or ensure your code works with either.
Bash: Not every Windows developer has a terminal that fully supports Bash, so it's generally preferred to write scripts in JavaScript instead of Bash.
Filename too long error: There is a 260 character limit for a filename when Git is compiled with msys. While the suggestions below are not guaranteed to work and could cause other issues, a few workarounds include:
Update Git configuration: git config --system core.longpaths true
Consider using a different Git client on Windows
