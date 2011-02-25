#!/usr/bin/env python -tt

"""SVN hooks APIs."""

import os

class SvnHooks:
    """SVN hooks API. Gets hook data, creates hook payload
       and calls sender.send_payload.
    """

    def __init__(self, sender):
        self._sender = sender

    @staticmethod
    def _svnlook(what, repos, rev):
        """Wrapper around svnlook tool."""

        with os.popen("svnlook %s -r %s %s" % \
                      (what, rev, repos), "r") as handler:
            return handler.readlines()

    def postcommit(self, repos, rev):
        """Postcommit hook."""

        # collect the info
        changed = self._svnlook("changed", repos, rev)
        log = self._svnlook("log", repos, rev)
        author = self._svnlook("author", repos, rev)
        date = self._svnlook("date", repos, rev)

        # prepare hook payload in the github payload format
        changes = {"A": [], "U": [], "D": []}
        for line in changed:
            oper, path = line.split()
            # Used oper[0] to work with 'UU' operation
            if oper[0] in changes:
                changes[oper[0]].append(path)

        payload = {"commits":
                   [
                       {"author": {"name": author, "email": ""},
                        "id": rev,
                        "added": changes["A"],
                        "modified": changes["U"],
                        "removed": changes["D"],
                        "message": log,
                        "timestamp": date
                        }
                       ]
                   }

        # send it
        self._sender.send_payload(payload)
