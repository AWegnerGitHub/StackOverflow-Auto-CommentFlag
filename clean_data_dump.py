import csv
from os import listdir

out_col_header = ["Comment Link", "text", "id", "CommentScore", "userid", "reputation", "posttypeid", "creationdate",
                  "commenttypeid"]

				  
def find_csv_filenames( path_to_dir, suffix=".csv" ):
	filenames = listdir(path_to_dir)
	return [ filename for filename in filenames if filename.endswith( suffix ) ]
	
filenames = find_csv_filenames("raw_data")

for name in filenames:
	with open('raw_data/%s' % (name), 'r') as f:
		with open('clean_data/clean_%s' % (name), 'wb') as o:
			reader = csv.reader(f)
			next(reader, None)  # Skip the headers line
			row_cnt = 0
			writer = csv.writer(o)
			writer.writerow(out_col_header)

			for row in reader:
				writer.writerow(
					["http://stackoverflow.com/posts/comments/%s" % (row[0]), row[1], row[2], row[3], row[4], row[5],
					 row[6], row[7], row[8]])
				row_cnt += 1

	print("Records Updated: %s" % (row_cnt))