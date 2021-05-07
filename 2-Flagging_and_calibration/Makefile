clean:
	rm -f *.pyc
	rm -f *.log *.last *.txt
	rm -f *.png

nocal: clean
	rm -f *.npy
	rm -rf *_fixvis.ms
	rm -rf *.G0 *.G0.*
	rm -rf *.K *.K.*
	rm -rf *.G *.G.*
	rm -rf *.B *.B.*

noimage: clean
	rm -f *.npy
	rm -rf *flux *image *psf *residual *model
	rm -rf *_split.ms

realclean: clean
	rm -f *.npy
	rm -rf *flux *image *psf *residual *model
	rm -rf *_fixvis.ms
	rm -rf *_split.ms
	rm -rf *.ms.*
	rm -rf *.G0 *.G0.*
	rm -rf *.K *.K.*
	rm -rf *.G *.G.*
	rm -rf *.B *.B.*

clobber: realclean
	rm -f *.pdf
	rm -rf *.ms

# -fin-
