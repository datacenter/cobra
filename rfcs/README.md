# Cisco ACI Programmability and Tools RFCs

This repo is a place to request for comments (rfc) for proposals related to
Cisco ACI programmability and tools.

The RFC process will be used to propose gather comments on design proposals,
branching strategies, release management, packaging mechanisms etc. Comments and
contributions on the rfcs are as valuable as code and documentation
contributions. Each RFC will have one owner who will be responsible for the
lifecycle of the document. We will follow the github fork/pull/review/merge
process to accept contributions.


## RFC Template

The RFC template file name is structured as <xxxx>-<name>.md where xxxx is a
four digit number, followed by a short name for the file. We will use
[github markdown](https://help.github.com/articles/markdown-basics/) format for
the RFC content.

### Document structure

#### Header

- Title: <document title>
- Author: <name>
- E-mail: <author email>
- Status: <Open, In-Progress, Closed>

#### Body

- Overview: Abstract overview of the proposal
- Motivation: Why is this needed? 
- Detail sections: Sections or chapters on each topic of the proposal
- Know Issues: Know issues and pitfalls with the proposed approach
- Drawbacks: Why should we *not* do this?
- Alternatives: Any alternatives considered and their strengths and weaknesses
  in our context
- Unresolved Items: Any unresolve items that require explicit feedback before
  we close the proposal

Here is an example [template](0000-template.md).

## Directory Structure

Pure text RFCs are checked in directly at the top level directory. In the
future, if we want RFCs to contain pictures and other media we can create a
directory with the <xxxx>-<name> template. This directory must contain a file
with <name>.md and can refer to other files within the directory

For example:

0000-template.md
0001-api/api.md
