congress-visualization
======================

USA Congress Visualizations

Instructions
------------

Download the information with the following command. This may take a long time.

    bash src/download-data.sh

Run the gridlock script for the House of Representatives and the Senate and
store its results in public/

    python src/gridlock.py h > public/representatives.json
    python src/gridlock.py s > public/senators.json

Launch your browser pointing to public/gridlock.html (notice that it might fail
on local if you use Chrome due ajax limitations).
