
from subprocess import check_output, TimeoutExpired, STDOUT, PIPE, CalledProcessError, Popen
from os import path, setsid, killpg
import signal

limit = 24*5  # time (hours) to process one subject, then the process is terminated (sometimes the freesurfer gets stuck)

def run_timeout(cmd, timeout, env):
    with Popen(cmd, stdout=PIPE, stderr=STDOUT, preexec_fn=setsid, env=env) as process:
        try:
            return process.communicate(timeout=timeout)[0]
        except TimeoutExpired:
            killpg(process.pid, signal.SIGINT)  # send signal to the process group
            raise TimeoutExpired(cmd, timeout)
            # return process.communicate()[0]


def load_result(log_file):
    with open(log_file, 'r') as hn:
        result_string = hn.readlines()[-1]
        return 'finished without error at' in result_string


def recon_subject(params):
    subject, t1, t2 = params[0], params[1], params[2]
    results_all_dir = '/mnt/e/output/segmented'  # user input
    svars = dict()
    svars['FREESURFER_HOME'] = '/usr/local/freesurfer'
    svars['SUBJECTS_DIR'] = results_all_dir
    svars['PATH'] = '/usr/local/freesurfer/bin:/usr/local/freesurfer/fsfast/bin:/usr/local/freesurfer/tktools:/usr/share/fsl/5.0/bin:/usr/local/freesurfer/mni/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/lib/fsl/5.0'
    svars['MINC_BIN_DIR'] = '/usr/local/freesurfer/mni/bin'
    svars['MNI_DIR'] = '/usr/local/freesurfer/mni'
    svars['MINC_LIB_DIR'] = '/usr/local/freesurfer/mni/lib'
    svars['MNI_DATAPATH'] = '/usr/local/freesurfer/mni/data'
    svars['PERL5LIB'] = '/usr/local/freesurfer/mni/share/perl5'

    path_surfer = '/usr/local/freesurfer/bin/recon-all'

    result_dir = path.join(results_all_dir, 's{}'.format(subject.zfill(5)))

    if not path.isfile(t1):
        raise ValueError('Source file {} was not found.'.format(t1))
    if t2 and not path.isfile(t2):
        raise ValueError('Source file {} was not found.'.format(t2))

    # jen T1
    # cmd_recon = [path_surfer, '-s', result_dir, '-i', t1, '-all', '-qcache']

    # T1 + FLAIR
    cmd_recon = [path_surfer, '-s', result_dir, '-i', t1, '-FLAIR', t2, '-FLAIRpial', '-no_t2pial', '-all', '-qcache']

    # T1 + T2
    # cmd_recon = [path_surfer, '-s', result_dir, '-i', t1, '-T2', t2, '-T2pial', '-all', '-qcache']

    try:
        run_timeout(cmd_recon, timeout=3600*limit, env=svars)
        log_file = path.join(result_dir, 'scripts', 'recon-all.log')
        return load_result(log_file)
    except CalledProcessError as e:
        # print(e.output)  # prilis dlouhe do konzole, v pripade potreby do souboru
        print('Some error occured for subject {}, see into log file.'.format(subject))
        return False
    except TimeoutExpired:
        print('Timeout expired for subject {}.'.format(subject))
        return False
