#Author-MigiBacon
#Description-


def copy(d):
    return dict(d)


_defaultKeyProps = {
    'x': 0, 'y': 0, 'x2': 0, 'y2': 0,                       # position
    'width': 1, 'height': 1, 'width2': 1, 'height2': 1,     # size
    'rotation_angle': 0, 'rotation_x': 0, 'rotation_y': 0,  # rotation
    'ghost': False, 'stepped': False, 'decal': False,       # miscellaneous options
    'sm': '', 'sb': '', 'st': '',                           # switch
    'labels': []
}

labelMap = [
    # 0  1  2  3  4  5  6  7  8  9 10 11   # align flags
    [ 0, 6, 2, 8, 9,11, 3, 5, 1, 4, 7,10], # 0 = no centering
    [ 1, 7,-1,-1, 9,11, 4,-1,-1,-1,-1,10], # 1 = center x
    [ 3,-1, 5,-1, 9,11,-1,-1, 4,-1,-1,10], # 2 = center y
    [ 4,-1,-1,-1, 9,11,-1,-1,-1,-1,-1,10], # 3 = center x & y
    [ 0, 6, 2, 8,10,-1, 3, 5, 1, 4, 7,-1], # 4 = center front (default)
    [ 1, 7,-1,-1,10,-1, 4,-1,-1,-1,-1,-1], # 5 = center front & x
    [ 3,-1, 5,-1,10,-1,-1,-1, 4,-1,-1,-1], # 6 = center front & y
    [ 4,-1,-1,-1,10,-1,-1,-1,-1,-1,-1,-1]  # 7 = center front & x & y
]

disallowedAlignmentForLabels = [
    [1,2,3,5,6,7],  #0
    [2,3,6,7],      #1
    [1,2,3,5,6,7],  #2
    [1,3,5,7],      #3
    [],             #4
    [1,3,5,7],      #5
    [1,2,3,5,6,7],  #6
    [2,3,6,7],      #7
    [1,2,3,5,6,7],  #8
    [4,5,6,7],      #9
    [],             #10
    [4,5,6,7]       #11
];


def defaultKeyProps():
    return copy(_defaultKeyProps)


def deserializeError(msg, data):
    raise Exception('{} {}'.format(msg, data))


def reorderLabelsIn(labels, align, skipdefault):
    ret = [ '', '', '', '', '', '', '', '', '', '', '', '']
    for i in range(1 if skipdefault else 0, len(labels)):
        ret[labelMap[align][i]] = labels[i];
        #print(i)
    return ret


def deserialize(rows):
    # Initialize with defaults
    current = defaultKeyProps()
    keys = []
    cluster = {'x': 0, 'y': 0}
    align = 4
    for r in range(len(rows)):
        if isinstance(rows[r], list):
            for k in range(len(rows[r])):
                key = rows[r][k]
                if isinstance(key, str):
                    newKey = copy(current);
                    newKey['width2'] = newKey['width'] if newKey['width2'] == 0 else newKey['width2']
                    newKey['height2'] = newKey['height'] if newKey['height2'] == 0 else newKey['height2']
                    newKey['labels'] = reorderLabelsIn(key.split('\n'), align, False);

                    # Add the key!
                    keys.append(newKey);

                    # Set up for the next key
                    current['x'] += current['width']
                    current['width'] = 1
                    current['height'] = 1
                    current['x2'] = 0
                    current['y2'] = 0
                    current['width2'] = 0 
                    current['height2'] = 0
                    current['stepped'] = False
                    current['decal'] = False

                else:
                    if 'r' in key:
                        if k != 0:
                            deserializeError("'r' can only be used on the first key in a row", key)
                        current['rotation_angle'] = key['r']

                    if 'rx' in key:
                        if k != 0:
                            deserializeError("'rx' can only be used on the first key in a row", key);
                        current['rotation_x'] = cluster['x'] = key['rx'];
                        current.update(cluster)

                    if 'ry' in key:
                        if k != 0:
                            deserializeError("ry' can only be used on the first key in a row", key);
                        current['rotation_y'] = cluster['y'] = key['ry'];
                        current.update(cluster)

                    if 'a' in key:
                        align = key['a']

                    if 'x' in key:
                        current['x'] += key['x']

                    if 'y' in key:
                        current['y'] += key['y']

                    if 'w' in key:
                        current['width'] = current['width2'] = key['w']

                    if 'h' in key:
                        current['height'] = current['height2'] = key['h']

                    if 'x2' in key:
                        current['x2'] = key['x2']

                    if 'y2' in key:
                        current['y2'] = key['y2']

                    if 'w2' in key:
                        current['width2'] = key['w2']

                    if 'h2' in key:
                        current['height2'] = key['h2']

                    if 'l' in key:
                        current['stepped'] = key['l']

                    if 'd' in key:
                        current['decal'] = key['d']

                    if 'g' in key:
                        current['ghost'] = key['g']

                    if 'sm' in key:
                        current['sm'] = key['sm']

                    if 'sb' in key:
                        current['sb'] = key['sb']

                    if 'st' in key:
                        current['st'] = key['st']

            # End of the row
            current['y'] += 1
        elif isinstance(rows[r], dict):
            if r != 0:
                raise Exception('Error: keyboard metadata must the be first element:')
        current['x'] = current['rotation_x'];
    return keys;