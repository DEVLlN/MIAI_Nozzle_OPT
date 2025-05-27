import argparse

parser = argparse.ArgumentParser(description='Process hits from a file')
parser.add_argument('input', metavar='input.slcio', type=str, help='List of input LCIO files', nargs="+")
parser.add_argument('-m', '--max_events', metavar='N', type=int, help='Maximum number of events to process', default=-1)
parser.add_argument('-o', dest='output', metavar='OUT.root', type=str, help='Path to the output ROOT file')
parser.add_argument('-s', '--skip_events', metavar='N', type=int, help='Number of events to skip', default=0)

opts = parser.parse_args()

from pyLCIO.io.EventLoop import EventLoop

#################################
# Importing the analysis driver #
#################################

# from drivers.trk_hits_mcp import TrkHitsMCPDriver as TheDriver
from drivers.cal_hits_mcp import CalHitsMCPDriver as TheDriver


########################################
# Running the driver over input events #
########################################

print('### Starting analysis with {0:d} input files:'.format(len(opts.input)))

evLoop = EventLoop()
for infile in opts.input:
    print('  {0:s}'.format(infile))
    evLoop.addFile(infile)
print('### Will store output in: {0:s}'.format(opts.output))
nEvents = evLoop.reader.getNumberOfEvents()
print('### Total number of events in the files: {0:d}'.format(nEvents))
driver = TheDriver(opts.output)
evLoop.add(driver)

if opts.max_events > 0:
	nEvents = opts.max_events

print('### Starting the loop over {0:d} events'.format(nEvents))
if opts.skip_events:
	print('### Skipping {0:d} events'.format(opts.skip_events))
	evLoop.skipEvents(opts.skip_events)
evLoop.loop(nEvents)
evLoop.printStatistics()
git 
print('### Finished')
