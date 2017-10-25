# visnormsc

**visnormsc** is a Graphical User Interface (GUI) for normalization of single-cell RNA sequencing (RNA-seq) data.

It is developed using the Python programming language so it is a cross-platform GUI program for Windows<sup>TM</sup>, Linux and macOS<sup>TM</sup>.

It depends on python >= 3.5 and following packages.

## Builtin package dependence:<br />
> copy<br />
> functools<br />
> io<br />
> math<br />
> multiprocessing<br />
> os<br />
> sys<br />
> time<br />
> tkinter<br />
> webbrowser<br />
> warnings<br />

## External package dependence:<br />
> matplotlib >= 2.0.2<br />
> numpy >= 1.12.1<br />
> pandas >= 0.20.1<br />
> scikit-learn >= 0.18.1<br />
> scipy >= 0.19.0<br />
> statsmodels >= 0.8.0<br />

## Installation:<br />
This software requires Python and additional packages installed on your platform before you can use it.

The easiest way to install the right Python version and dependencies is to download and install the latest version of [Anaconda](https://www.continuum.io/downloads) suitable for your platform.

After you successfully install Anaconda, in the CMD prompt on Windows<sup>TM</sup>, or in the terminal on Linux or macOS<sup>TM</sup>, type<br />
`python visnormscGUI.py`<br />
and then you can enjoy this GUI program.

If you encounter error like \"unknown command python\" then you need to check if you have installed Anaconda correctly and allowed the installation wizard to add python to your system environment path at the end of the installation.

Another optional way is to create the same conda environment as the one used for delevoping visnormsc. After conda installation, run<br />
`conda env create -f sharedCondaEnv.yml`<br />
where the *sharedCondaEnv.yml* file is under directory **bin**. The new environment can then be activated by, for example,<br />
`source activate visnormsc` in Linux and macOS, or<br/>
`activate visnormsc` in Windows.

## Wiki:<br />
A complete user manual is given at the [wiki page](https://github.com/solo7773/visnormsc/wiki).