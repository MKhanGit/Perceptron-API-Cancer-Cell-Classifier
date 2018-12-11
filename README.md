# Machine Learning Malignat Cell Classifier with Python & mongoDB
This project is an interactive applet for a python based neural network which has been trained on ~700 records of benign and malignant tumor cells. It randomly shuffles a deck of cell measurements and display them to the user, who can then pass them through the previously trained network, which attempts to classify each cell as "benign" or "malignant". All backend computation and fetching is done via python and mongoDB.

## Deployed Example
For a deployed demo, please visit https://theoryofgravity.ca/mongo/cells/ 

## Data Background
Attribute Information:

1. Sample code number: id number 
2. Clump Thickness: 1 - 10 
3. Uniformity of Cell Size: 1 - 10 
4. Uniformity of Cell Shape: 1 - 10 
5. Marginal Adhesion: 1 - 10 
6. Single Epithelial Cell Size: 1 - 10 
7. Bare Nuclei: 1 - 10 
8. Bland Chromatin: 1 - 10 
9. Normal Nucleoli: 1 - 10 
10. Mitoses: 1 - 10 
11. Class: (2 for benign, 4 for malignant)

Data Set Information:

Samples arrive periodically as Dr. Wolberg reports his clinical cases. The database therefore reflects this chronological grouping of the data. This grouping information appears immediately below, having been removed from the data itself: 

Group 1: 367 instances (January 1989) 

Group 2: 70 instances (October 1989) 

Group 3: 31 instances (February 1990) 

Group 4: 17 instances (April 1990) 

Group 5: 48 instances (August 1990) 

Group 6: 49 instances (Updated January 1991) 

Group 7: 31 instances (June 1991) 

Group 8: 86 instances (November 1991) 

----------------------------------------- 
Total: 699 points (as of the donated datbase on 15 July 1992) 

Note that the results summarized above in Past Usage refer to a dataset of size 369, while Group 1 has only 367 instances. This is because it originally contained 369 instances; 2 were removed. The following statements summarizes changes to the original Group 1's set of data: 

##### Group 1 : 367 points: 200B 167M (January 1989) 

##### Revised Jan 10, 1991: Replaced zero bare nuclei in 1080185 & 1187805 

##### Revised Nov 22,1991: Removed 765878,4,5,9,7,10,10,10,3,8,1 no record 
##### : Removed 484201,2,7,8,8,4,3,10,3,4,1 zero epithelial 
##### : Changed 0 to 1 in field 6 of sample 1219406 
##### : Changed 0 to 1 in field 8 of following sample: 
##### : 1182404,2,3,1,1,1,2,0,1,1,1


Relevant Papers:

Wolberg, W.H., & Mangasarian, O.L. (1990). Multisurface method of pattern separation for medical diagnosis applied to breast cytology. In Proceedings of the National Academy of Sciences, 87, 9193--9196. 
[Web Link] 

Zhang, J. (1992). Selecting typical instances in instance-based learning. In Proceedings of the Ninth International Machine Learning Conference (pp. 470--479). Aberdeen, Scotland: Morgan Kaufmann. 
[Web Link]
