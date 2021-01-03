from ycmd.completers.completer import Completer
from ycmd.completers.general.filename_completer import FilenameCompleter
from ycmd import responses
import ycmd.completers.completer_utils as cutils
import subprocess
import re


class CMakeCompleter(Completer):
    """
    A cmake completer.
    """

    def __init__(self, user_options):
        super().__init__(user_options)
        self._candidate = []
        self._raw_names = {}
        self._fn_compl = FilenameCompleter(user_options)
        for type in ['command', 'variable', 'property', 'module']:
            ret = subprocess.run(['cmake', '--help-{}-list'.format(type)], capture_output=True)
            if ret.returncode == 0:
                cmds = ret.stdout.decode().split()
                self._raw_names.update([(cmd, type) for cmd in cmds])
                self._candidate += [
                    responses.BuildCompletionData(
                        cmd, kind=type[0]) for cmd in cmds]

    def ShouldUseNowInner(self, request_data):
        if len(self._candidate) == 0:
            return False
        # dont complete when is filename
        if self._fn_compl.ShouldUseNow(request_data):
            return False
        else:
            return self.QueryLengthAboveMinThreshold(request_data)

    def ComputeCandidates(self, request_data):
        if not self.ShouldUseNow(request_data):
            return []
        query = self._GetQueryWord(request_data)
        return self.FilterAndSortCandidates(self._candidate, query)

    def SupportedFiletypes(self):
        return ['cmake']

    def GetSubcommandsMap(self):
        return {
                'GetDoc': (lambda self, request_data, args:
                    self._GetDoc(request_data, args))
        }

    def _GetQueryWord(self, request_data):
        line = request_data['line_value']
        start_point = request_data['start_codepoint'] - 1
        line = line[start_point:]
        m = re.match(r'(\w+).*', line)
        if m is None:
            query = ''
        else:
            query = m.group(1)
        return query

    def _GetDoc(self, request_data, args):
        query = self._GetQueryWord(request_data)
        if query in self._raw_names: 
            type = self._raw_names[query]
            ret = subprocess.run(
                    ['cmake', '--help-{}'.format(type), query],
                    capture_output=True)
            if ret.returncode == 0:
                msg = ret.stdout.decode()
                return responses.BuildDetailedInfoResponse(str(request_data))

        msg = "Can't find doc for {}".format(query)
        return responses.BuildDisplayMessageResponse(msg)

