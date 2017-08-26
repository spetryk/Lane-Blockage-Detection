% Testing scatterplot

sz = 5;

figure
hold on
xticks([0 7200 14400 21600 28800 36000 43200 50400 57600 64800])
xticklabels({'12 AM', '2 AM', '4 AM', '6 AM', '8 AM', '10 AM', '12 PM',...
    '2 PM', '4 PM', '6 PM'})
yticks([0 1 2 3 4 5])
yticklabels({'No Information', 'Uncongested', 'Light', 'Moderate', ...
    'Heavy', 'Lane Blockage'})

scatter(Time,Left,'rs');
scatter(Time,Through,'bo');
scatter(Time,Right,'g^');
scatter(Time,ThroughQSB,'o','MarkerFaceColor','b');
scatter(Time,RightQSB,sz,'g^','filled');

hold off
