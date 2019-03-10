## About
This is improved version of V6Gene generator. 
* Now random generate process is used just for generating `RIR` prefixes and 
called at the start  of the program. 

* After that trie traversal generating process is started. 
 
* Unlike V6gene , generator can generate prefixes from prefixes that were added to trie during generating process. 

* New `EU` prefixes could be generated from `LIR` or `ISP` prefixes.

* This version of generator works better with level distribution parameter.

* `level_distribution` was changed to `max_level` and just specify maximum possible level for trie.

## Usage 
* CLI
```
python3 IPv6Gene.py --depth_distribution 0:<int>,1:<int>,2:<int>...64:<int> --input <path to input seed file> --prefix_quantity <int> --max_level <int>
```


## Input parameters
- `depth_distribution` - output (requested) depth distribution
- `input` - seed prefix file which contains prefixes which will be added to binary trie
- `prefix_quantity` - number of prefixes in binary trie after generating process 
- `max_level` - specify max possible level for binary trie


## Example

```
python3 IPv6Gene.py --depth_distribution 0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:1,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:1,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,42:0,43:0,44:0,45:1,46:0,47:0,48:0,49:0,50:0,51:0,52:0,53:0,54:0,55:0,56:0,57:0,58:1,59:0,60:0,61:0,62:0,63:0,64:1 --input test.dms --prefix_quantity 5 --level_distribution 0:10,1:1,2:3,3:0,4:0,5:0

```