#!/usr/bin/env python -tt

import os, re
from datetime import datetime

"""GIT hooks APIs."""


EMAIL_RE = re.compile("^(.*) <(.*)>$")


def _get_revlist(old, new):
    with os.popen("git rev-list --pretty=medium %s..%s" % (old, new), "r") as handler:
        return handler.read()


def _get_commits(old, new):
    revlist = _get_revlist(old, new)
    sections = revlist.split('\n\n')[:-1]

    commits = []
    index = 0
    while index < len(sections):
        lines = sections[index].split('\n')

        # first line is 'commit HASH\n'
        props = {'id': lines[0].strip().split(' ')[1]}

        # read the header
        for line in lines[1:]:
            key, val = line.split(' ', 1)
            props[key[:-1].lower()] = val.strip()

        # read the commit message
        props['message'] = sections[index+1]

        # use github time format
        basetime = datetime.strptime(props['date'][:-6], "%a %b %d %H:%M:%S %Y")
        tzstr = props['date'][-5:]
        props['date'] = basetime.strftime('%Y-%m-%dT%H:%M:%S') + tzstr

        # split up author
        author = EMAIL_RE.match(props['author'])
        if author:
            props['name'] = author.group(1)
            props['email'] = author.group(2)
        else:
            props['name'] = 'unknown'
            props['email'] = 'unknown'
        del props['author']

        # increment the counter
        index += 2

        commits.append({
            'id': props['id'],
            'author': {'name': props['name'], 'email': props['email']},
            'message': props['message'],
            'timestamp': props['date']
        })

    return commits


class GitHook(object):

    def __init__(self, sender):
        self._sender = sender

    def postreceive(self, old, new, ref):
        """Postcommit hook."""
        self._sender.send_payload({
            "before": old,
            "after": new,
            "ref": ref,
            "repository": {
                "url": "",
                "name": "",
                "description": "",
                "owner": {
                    "email": "",
                    "name": ""
                }
            },
            "commits": _get_commits(old, new),
        })
