import pathlib


if __name__ == '__main__':
    for d in pathlib.Path('dist').glob('ipset_c.tar.gz'):
        d.unlink()
    for d in pathlib.Path('dist').glob('*.tar.gz'):
        d.rename('dist/ipset_c.tar.gz')
