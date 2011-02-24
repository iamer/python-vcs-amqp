#!/usr/bin/env python -tt

import os

"""SVN hooks APIs."""

class SvnHookPayload:
    """
    Prepares hook payload in the github payload format:
    https://github.com/github/github-services/blob/master/docs/github_payload
    """

    def __init__(self, rev, author, log, changed, date):
        self._rev = rev
        self._author = author
        self._log = log
        self._changed = changed
        self._date = date

    @property
    def payload(self):
        """Get payload in github_payload format."""
           
        changes = {"A": [], "U": [], "D": []}
        for line in self._changed:
            oper, path = line.split()
            # Used oper[0] to work with 'UU' operation
            if oper[0] in changes:
                changes[oper[0]].append(path)                

        return {"commits":
                [
                    {"author": {"name": self._author, "email": ""},
                     "id": self._rev,
                     "added": changes["A"],
                     "modified": changes["U"],
                     "removed": changes["D"],
                     "message": self._log,
                     "timestamp": self._date
                    }
                ]
                }


class SvnHooks:
    """SVN hooks API. Gets hook data, creates hook payload object
       and calls sender.send_payload.
    """

    def __init__(self, sender):
        self._sender = sender

    @staticmethod
    def _svnlook(what, repos, rev):
        """Wrapper around svnlook tool."""
        with os.popen("svnlook %s -r %s %s" % (what, rev, repos), "r") as handler:
            return handler.readlines()
    
    def postcommit(self, repos, rev):
        """Postcommit hook."""

        # collect the info
        changed = self._svnlook("changed", repos, rev)
        log = self._svnlook("log", repos, rev)
        author = self._svnlook("author", repos, rev)
        date = self._svnlook("date", repos, rev)

        # prepare payload
        payload = SvnHookPayload(rev, author, log, changed, date)

        # send it
        self._sender.send_payload(payload)

