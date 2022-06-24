import os
import os.path as path
import glob
import re
import shutil
import colorama

colorama.init()
cg = colorama.Fore.GREEN
cr = colorama.Fore.LIGHTRED_EX
cc = colorama.Fore.CYAN
cw = colorama.Fore.WHITE
cbb = colorama.Style.BRIGHT
cd = colorama.Style.RESET_ALL

class RealFile:
    def __init__(self, relative_path: str, base_path: str):
        self.base_path = base_path
        self.orig_path = relative_path.replace('\\', '/').strip('/')
        self.type_path = re.sub('_run-\d{2}', '', self.orig_path)
        run = re.search('_run-\d{2}', self.orig_path)
        self.version = run.group(0) if run else ''

    def __str__(self):
        run = f' ({self.version})' if self.version else ''
        return self.type_path + run

    def get_full_path(self):
        return path.join(self.base_path, self.orig_path)

    def exists(self):
        return path.isfile(self.get_full_path())

    def copy_to(self, dst: str):
        src_file = self.get_full_path()
        dst_dir = path.dirname(dst)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copyfile(src_file, dst)
        print(f'copy {cc}{src_file}{cd} -> {cc}{dst}{cd}')

class RequestedFile:
    def __init__(self, definiton: str):  # line in config file
        self.requested, self.searched = definiton.split(':')

    def match_for_subj(self, subj_id: str, real_file: RealFile):
        return re.fullmatch(self.searched.replace('{subjId}', subj_id), real_file.type_path)

    def __str__(self):
        return self.searched + ' -> ' + self.requested

class IndividualRule:
    def __init__(self, definiton: str, base_path: str):  # line in config
        self.subj_id, self.requested, assigned = definiton.split(':')
        self.assigned = RealFile(assigned, path.join(base_path, self.subj_id))

class IndividualSpec:
    def __init__(self, ref_global: list):  # [RequestedFile]
        self.spec = {}
        self.ref_global = ref_global

    def add(self, rule: IndividualRule, index: int):
        if not rule.assigned.exists():
            raise SystemExit(f'Error in individual rules, the file {cc}\'{rule.assigned.orig_path}\'{cd} for subj {cc}{rule.subj_id}{cd} (line {cc}{index + 1}{cd}) was not found.')
        if not any([g.requested == rule.requested for g in self.ref_global]):
            raise SystemExit(f'Error in individual rules, the key {cc}\'{rule.requested}\'{cd} (line {cc}{index + 1}{cd}) is not contained in global rules.')
        subj_dict = self.spec.setdefault(rule.subj_id, {})
        if rule.requested in subj_dict:
            raise SystemExit(f'Error in individual rules, the key {cc}\'{rule.requested}\'{cd} for subj {cc}{rule.subj_id}{cd} is not unique.')
        subj_dict[rule.requested] = rule

    def has(self, subj_id: str, global_rule: RequestedFile):
        if not subj_id in self.spec:
            return False
        if not global_rule.requested in self.spec[subj_id]:
            return False
        return True

    def get(self, subj_id: str, global_rule: RequestedFile):
        return self.spec[subj_id][global_rule.requested]

class CopyPair:
    def __init__(self, dst_rule: RequestedFile, src_file: RealFile):
        self.src = src_file
        self.dst = dst_rule

    def copy_to(self, dst_base_path: str):
        self.src.copy_to(path.join(dst_base_path, self.dst.requested))

class Ambiguous:
    def __init__(self, rule: RequestedFile, matches: list):  # [RealFile]
        self.rule = rule
        self.matches = matches
        self.same_type = True
        self.versions = []
        self.process_type()

    def process_type(self):
        for match in self.matches:
            self.versions.append(match.version)
            if match.type_path != self.matches[0].type_path:
                self.same_type = False

    def has_same_type(self):
        return self.same_type

    def get_versions(self):
        if not self.same_type:
            raise ValueError()
        return self.versions

    def get_common_path(self):
        if not self.same_type:
            raise ValueError()
        return self.matches[0].type_path

    def get_raw_files(self):
        return [item.orig_path for item in self.matches]

class SubjRelation:
    def __init__(self, subj_id: str, rules: list, individual: IndividualSpec, files: list):  # [RequestedFile], [RealFile]
        self.subj_id = subj_id
        self.ok_copy = []
        self.error_missing = []
        self.error_ambiguous = []
        self.match_files(rules, individual, files)

    def match_files(self, rules: list, individual: IndividualSpec, files: list):  # [RequestedFile], [RealFile]
        for rule in rules:
            if individual.has(self.subj_id, rule):
                self.ok_copy.append(CopyPair(rule, individual.get(self.subj_id, rule).assigned))
            else:
                matches = []
                for rfile in files:
                    if rule.match_for_subj(self.subj_id, rfile):
                        matches.append(rfile)
                count_found = len(matches)
                if count_found == 1:
                    self.ok_copy.append(CopyPair(rule, matches[0]))
                elif count_found == 0:
                    self.error_missing.append(rule)
                else:
                    self.error_ambiguous.append(Ambiguous(rule, matches))

    def report(self):
        if not self.error_missing and not self.error_ambiguous:
            print(f'{cbb}{self.subj_id}{cd} - {cg}ok{cd}')
        else:
            print(f'{cbb}{self.subj_id}{cd} - {cr}error{cd}')
            for missing in self.error_missing:
                print(f' - {missing.requested} is missing, no file match pattern {missing.searched}')
            for ambiguous in self.error_ambiguous:
                if ambiguous.has_same_type():
                    str_versions = f'\'{cd}, {cc}\''.join(ambiguous.get_versions())
                    print(f' - {cc}{ambiguous.rule.requested}{cd} is ambiguous, file {cc}{ambiguous.get_common_path()}{cd}'
                        + f' exists in following versions: {cc}\'{str_versions}\'{cd}')
                else:
                    str_files = ', '.join(ambiguous.get_raw_files())
                    print(f' - {ambiguous.rule.requested} is ambiguous, following files match pattern: {str_files}')

    def get_for_copy(self):
        return self.ok_copy

def load_global_rules(filename: str):
    rules = []
    with open(filename) as hn:
        for line in hn:
            line = line.strip()
            if line and not line.startswith(';'):
                rules.append(RequestedFile(line))
    return rules

def load_individual_rules(filename: str, raw_dir: str, ref_global: list):  # [RequestedFile]
    individual = IndividualSpec(ref_global)
    with open(filename) as hn:
        for index, line in enumerate(hn):
            line = line.strip()
            if line and not line.startswith(';'):
                individual.add(IndividualRule(line, raw_dir), index)
    return individual

def list_files(subj_dir: str):
    all_files = []
    for root, dirs, files in os.walk(subj_dir):
        for item in files:
            rel_path = path.join(root, item).replace(subj_dir, '')
            all_files.append(RealFile(rel_path, subj_dir))
    return all_files

def copy_to(copy_pairs: list, dst_base_path: str):  # [CopyPair]
    for cfile in copy_pairs:
        cfile.copy_to(dst_base_path)

# TODO: v individualni specifikaci umoznit pouze verzi (odlisi se apostrofy), soubort se dohleda globalnim pravidelm, snizi se pravdepodobnost preklepu

def main():
    subjs = []
    global_rules = '***/rules_global.txt'
    individual_rules = '***/rules_individual.txt'
    raw_dir = '***'
    dst_dir = '***'

    rules = load_global_rules(global_rules)
    specification = load_individual_rules(individual_rules, raw_dir, rules)

    for subj_id in subjs:
        subj_dir = path.join(raw_dir, subj_id)
        files = list_files(subj_dir)

        relation = SubjRelation(subj_id, rules, specification, files)
        relation.report()

        if False:
            copy_to(relation.get_for_copy(), path.join(dst_dir, subj_id))

main()
