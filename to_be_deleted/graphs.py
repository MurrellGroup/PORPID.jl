from collections import namedtuple, defaultdict
try:
    import matplotlib as mpl
#    mpl.use('Agg')
    from matplotlib import pyplot as plt
except ImportError:
    print("Matplotlib does not seem to be available. Try 'pip install matplotlib'\nError:")
    raise
try:
    import numpy as np
except ImportError:
    print("Numpy does not seem to be available. Try 'pip install numpy'\nError:")
    raise
import argparse

def log_tag_dist(input_file, line_order=["id"], threshold=None):
    tag_dist(input_file, line_order, threshold, loglog=True)

def tag_dist(input_file, line_order=["id"], threshold=None, loglog=False):
    if "id" not in line_order:
        print("Tag distribution needs id's")
        return

    tags = defaultdict(lambda: 0)
    for line in input_file:
        parts = line.strip().split()
        if len(parts) != len(line_order):
            continue
        if threshold is not None and "likelihood" in line_order:
            likelihood = float(parts[line_order.index("likelihood")])
            if likelihood < threshold:
                continue
        barcode = parts[line_order.index("id")]
        tags[barcode] += 1
    max_count = 0
    max_count_tag = None
    count_dist = defaultdict(lambda: 0)
    for tag, count in tags.items():
        if count > max_count:
            max_count = count
            max_count_tag = tag
        count_dist[count] += 1
    plt.figure(figsize=(30, 5), dpi=300)
    print("Most common tag: " + str(max_count_tag) + " appears " + str(max_count) +" times")
    if max_count <= 1000:
        count_counts = [np.log2(count_dist[i]) for i in range(1, max_count + 1)]
        bars = plt.bar(range(np.log2(max_count)), count_counts, width=1.0, linewidth=0, log=True)
        plt.ylim(0.1)
        xtick_spacing = max(1, int(round(max_count / 250.0) * 5))
        if loglog:
            plt.xticks([xtick_spacing/2.0 + x for x in range(0, max_count, xtick_spacing)], [r'$2^{{{0}}}$'.format(x) for x in range(0, max_count, xtick_spacing)], rotation='vertical')
        else:
            plt.xticks([xtick_spacing/2.0 + x for x in range(0, max_count, xtick_spacing)], range(0, max_count, xtick_spacing), rotation='vertical')
    else:
        num_bins = 250
        array = list(tags.values())
        xtick_spacing = max(1, int(round(max_count / 250.0) * 5))
        if loglog:
            max_count = int(np.log2(max_count))
            array = np.array(np.log2(array))
        n, bins, patches = plt.hist(array, num_bins, log=True)
        plt.ylim(0.1)
        if loglog:
            plt.xticks([xtick_spacing/2.0 + x for x in range(0, max_count, xtick_spacing)], [r'$2^{{{0}}}$'.format(x) for x in range(0, max_count, xtick_spacing)], rotation='vertical')
    if loglog:
        plt.xlabel('Floor(log2(number of copies in bin))')
    else:
        plt.xlabel('Number of copies in bin')
    plt.ylabel('Unique ID\'s with bin size')
    plt.savefig('bin_sizes')
    #plt.show()
    plt.cla()

def likelihood_cutoffs(input_file, line_order=["likelihood"]):
    num_bins = 50
    if "likelihood" not in line_order:
        print("Likelihood cutoff needs a likelihood score")
        return
    templates = defaultdict(list)
    for line in input_file:
        parts = line.strip().split()
        if len(parts) != len(line_order): continue
        likelihood = float(parts[line_order.index("likelihood")])
        templates["All"].append(likelihood)
        if "template" in line_order:
            template = parts[line_order.index("template")]
            templates[template].append(likelihood)
    for template, scores in sorted(templates.items()):
        n, bins, patches = plt.hist(scores, num_bins)
        plt.xlabel('Likelihood')
        plt.ylabel('Frequency')
        plt.title(template)
        plt.savefig(template)
        #plt.show()
        plt.cla()

def comparative_likelihood(input_file, line_order=["template", "likelihood"]):
    num_bins = 50
    if "likelihood" not in line_order or "template" not in line_order:
        print("Comparative likelihood needs templates and likelihood scores")
        return
    relative_score = defaultdict(list)
    group = []
    best_score = float("-Inf")
    best_template = None
    for line in input_file:
        parts = line.strip().split()
        if len(parts) != len(line_order):
            # Ending a group
            if len(group) == 0: # There hasn't been a group yet
                continue
            for template, score in group:
                relative_score[(best_template, template)].append(score)
            # Reset group
            group = []
            best_score = float("-Inf")
            best_template = None
            continue

        template = parts[line_order.index("template")]
        score = float(parts[line_order.index("likelihood")])
        if score > best_score:
            best_score = score
            best_template = template
        group.append((template, score))

    others = defaultdict(list)
    for winner, other in relative_score.keys():
        others[winner].append(other)

    for winner in others.keys():
        print(winner)
        for other in others[winner]:
            data = np.array(relative_score[(winner, other)])
            y,binEdges=np.histogram(data, bins=50)
            bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
            plt.plot(bincenters, y ,'-', label=other)
        plt.xlabel('Likelihood')
        plt.ylabel('Frequency')
        plt.title(winner)
        plt.legend(loc='upper left')
        #plt.savefig(winner)
        plt.show()
        plt.cla()
        
def error_cutoffs(input_file, line_order=["errors"]):
    num_bins = 40
    if "errors" not in line_order:
        print("Error cutoff needs an error count")
        return
    templates = defaultdict(list)
    for line in input_file:
        parts = line.strip().split()
        if len(parts) != len(line_order): continue
        errors = int(parts[line_order.index("errors")])
        templates["All"].append(errors)
        if "template" in line_order:
            template = parts[line_order.index("template")]
            templates[template].append(errors)
    for template, errors in sorted(templates.items()):
        n, bins, patches = plt.hist(errors, num_bins)
        plt.xlabel('Errors')
        plt.ylabel('Frequency')
        plt.title(template)
        plt.savefig(template)
        #plt.show()
        plt.cla()

parser = argparse.ArgumentParser(description="Get info on PrimerID results")
parser.add_argument('command', type=str, choices=["log_tag_dist", "tag_dist", "likelihoods", "comparative", "errors"], default="tag_dist")
parser.add_argument('input', type=argparse.FileType('r'), help="the location of primer id results file to visualise")
parser.add_argument('-f', '--format', metavar='keyword', action='append', choices=["template", "id", "likelihood", "errors"], help='The format of the lines')
parser.add_argument('-t', '--threshold', type=float, help='Likelihood threshold below which lines are ignored')
args = parser.parse_args()

if args.command == "log_tag_dist":
    if args.format is not None and args.threshold is not None:
        log_tag_dist(args.input, args.format, args.threshold)
    elif args.format is not None:
        log_tag_dist(args.input, args.format)
    else:
        log_tag_dist(args.input)
if args.command == "tag_dist":
    if args.format is not None and args.threshold is not None:
        tag_dist(args.input, args.format, args.threshold)
    elif args.format is not None:
        tag_dist(args.input, args.format)
    else:
        tag_dist(args.input)
elif args.command == "likelihoods":
    if args.format is not None:
        likelihood_cutoffs(args.input, args.format)
    else:
        likelihood_cutoffs(args.input)
elif args.command == "comparative":
    if args.format is not None:
        comparative_likelihood(args.input, args.format)
    else:
        comparative_likelihood(args.input)
elif args.command == "errors":
    if args.format is not None:
        error_cutoffs(args.input, args.format)
    else:
        error_cutoffs(args.input)
