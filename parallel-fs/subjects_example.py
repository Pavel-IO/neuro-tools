import os.path as path

def get_list():
  input_dir = '/mnt/e/input'
  subjs = [
    '001E', '002E', '003E', '004E', '005E', '006E', '007E', '008E', '009E', '010E',
    '011E', '012E', '013E', '014E', '015E', '016E', '017E', '018E', '019E', '020E',
  ]
  output = []
  for subj in subjs:
      output.append([subj, input_dir + '{}/_{}_t1.nii'.format(subj, subj), input_dir + '{}/_{}_t2.nii'.format(subj, subj)])
  return output


def check_exists():
    for line in get_list():
        if not path.isfile(line[1]):
            print('{} was not found.'.format(line[1]))
        if not path.isfile(line[2]):
            print('{} was not found.'.format(line[2]))


if __name__ == '__main__':
    check_exists()
