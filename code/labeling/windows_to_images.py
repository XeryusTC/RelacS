import h5py
import os

import numpy as np

#wins:          windows that will be used to generate images
#percentage:    percentage of files used to generate training data vs validation data
def toImageData(wins, percentage):
    if percentage > 1 or percentage < 0:
        RuntimeError('Percentage should be between 0 and 1')

    totallen = 0
    for f in wins:
        totallen  = totallen  + len(wins[f])

    trainlen = int(totallen*percentage)
    validlen = totallen - trainlen

    sample = wins.values()[0][0]
    winlen = sample['end'] - sample['start']

    train_frags = np.empty([trainlen, 109, winlen])
    train_flags = np.empty([trainlen, 3])

    valid_frags = np.empty([validlen, 109, winlen])
    valid_flags = np.empty([trainlen, 3])

    filedir = os.path.join(os.getcwd(), 'hdf5')

    counter = 0
    train_skipcount = 0
    valid_skipcount = 0

    for f in wins:
        filename = os.path.join(filedir, f)
        filepointer = h5py.File(filename, 'r')
            
        for window in wins[f]:

            # create image from window
            beg = int(window['start'])
            end = int(window['end'])
            
            scale = filepointer.attrs.get('scale', [0, 60])

            fragment = filepointer['energy'][:, beg:end]
            if train_frags[0,:,:].shape != fragment.shape :
                if counter <= trainlen:
                    train_skipcount += 1
                else :
                    valid_skipcount += 1
                #Skip fragments with unexpected shape ( not frags[0,:,:].shape ) 
                continue;
            
            
            # create array of corresponding output flags
            flagment = np.array([1.0 if window['stressful'] else 0.0, 
                1.0 if window['relaxing'] else 0.0,
                1.0 if window['sudden'] else 0.0])

            
            # add to train or validation set
            if counter < trainlen:
                train_frags[counter, :, :] = fragment
                train_flags[counter, :] = flagment
            else :
                valid_frags[counter - trainlen, :, :] = fragment
                valid_flags[counter - trainlen, :] = flagment

            counter += 1
            skipcount = train_skipcount + valid_skipcount

            totcount = counter + skipcount
            progress = (totcount / float(totallen))
            loadbar = '#' * int(round(20*progress)) +  ' ' * int(round(20*(1-progress)))

            print '\r[{0}] {1}% of {2} windows processed, {3} windows skipped'.format(loadbar, 
                int(round(100*progress)),
                totallen,
                skipcount),
    print #this is a newline
    train_g = train_frags[:trainlen-train_skipcount, :]
    train_l = train_flags[:trainlen-train_skipcount, :]
    valid_g = valid_frags[:validlen-valid_skipcount, :] 
    valid_l = valid_flags[:validlen-valid_skipcount, :]
    return train_g, train_l, valid_g, valid_l
     

#fig, ax = plt.subplots(figsize=(20,4))
#image = ax.imshow(filepointer['energy'][:,beg:end], aspect='auto', interpolation='none', origin='bottom')
#fig.colorbar(image)
#plt.show()
            
