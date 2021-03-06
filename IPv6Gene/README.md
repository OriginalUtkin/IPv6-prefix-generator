## About
This is improved version of V6Gene generator. 

* There are no exist allocation politics for prefixes with length less than 12. Generator can't generate them and can't generate new prefixes from them. But this prefixes could be found in seed prefix file and could be added to the binary trie during construct binary trie process.

* Now random generate process is used just for generating `RIR` prefixes and 
called at the start  of the program. All randomly generated prefixes were added to trie and could be used in trie traversal generating phase as well.

* After that trie traversal generating process is started. 
 
* Unlike V6gene , new version of generator can generate prefixes from prefixes that were added to trie during generating process. 

* New `EU` prefixes could be generated from `LIR` or `ISP` prefixes.

* `level_distribution` input argument was simplified. Now would be enough just specify required maximum trie level using `max_level` input argument that is used instead of `level_distribution`.

* `RGR` input argument was removed. Script automatically calculate number of prefixes that will be generated randomly according to `depth_distribution`

## Usage 
* CLI
```
python3 IPv6Gene.py --depth_distribution 0:<int>,1:<int>,2:<int>...64:<int> --input <path to input seed file> --prefix_quantity <int> --max_level <int>
```
 or using files with specified depth distribution
 

## Input arguments
- `depth_distribution` - output (requested) depth distribution

- `input` - seed prefix file which contains prefixes which will be added to binary trie and will be used for generating new prefixes

- `prefix_quantity` - number of prefixes after generating process in binary trie

- `max_level` - specify max possible level for binary trie

- `depth_distribution_path` - Specify path to the file which contains depth distribution data. Sample file could be found in the
                        `input_params/IPv6Gene folder`. This argument can't be combined with `depth_distribution` argument. If not
                        given, `depth_distribution` is required. 


## Example
`input` and `IPv6Gene.py` files are in main project folder ; test dataset is in `dataset` folder;
```
python3 IPv6Gene.py --depth_distribution 0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:1,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:1,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,42:0,43:0,44:0,45:1,46:0,47:0,48:0,49:0,50:0,51:0,52:0,53:0,54:0,55:0,56:0,57:0,58:1,59:0,60:0,61:0,62:0,63:0,64:1 --input dataset/test_data/test_v6Generator.dms --prefix_quantity 5 --max_level 5

```
or using file with specified depth distribution
 ```
 python3 IPv6Gene.py --input dataset/test_data/test_v6Generator.dms --depth_distribution_path input_params/IPv6Gene/input_depth  --prefix_quantity 4 --max_level 5 --output output.txt
```