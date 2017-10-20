clear
clc
htable = readtable('result1.csv');

stable = readtable('scores.csv');

dat = [htable(:, 3), stable(:,2)];

l = height(dat);
list = [];
for x= 1:l 
    if string(dat{x, 1}) == 'N/A'
       list = [list x];
    end 
end

dat(list, :) = [];  
l = height(dat);

v1 = table2array(dat(:, 1));
v1 =    cellfun(@str2double,v1);

v2 = table2array(dat(:, 2));

[RHO1,PVAL1] = corr(v1,v2,'Type','Spearman');

[RHO2,PVAL2] = corr(v1,v2,'Type','Pearson');

[RHO3,PVAL3] = corr(v1,v2,'Type','Kendall');



rank1 = floor(tiedrank(v1));

rank2 = floor(tiedrank(v2));


[RHO4,PVAL4] = corr(rank1,rank2,'Type','Spearman');


figure
scatter(v1,v2, 'filled')
title('H-indexes and PageRank scores')
xlabel('h-index')
ylabel('PageRank score')