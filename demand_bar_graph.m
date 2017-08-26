% plot bar graph of demand data

% Critical occupancy demand

figure
hold on
xlim([-1 24]);
xlabel('Hour');
ylabel('Vehicles per hour');
set(gca,'FontSize',14);

x = [0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23];
y = [60 120 180 240 300 360 420 480 540 600 660 720 780 840 900 960 ...
    1020 1080 1080 1080 1080 1080 1080 1080];

bar(x,y, 'FaceColor', [169 169 169]./255);
 
hold off

% Section 826 demand

% figure
% hold on
% xlim([-1 19]);
% xlabel('Hour');
% ylabel('Percent of OD matrix applied');
% set(gca,'FontSize',14);
% 
% y = [100 75 75 50 10 10;...
%     125 125 125 125 125 125;...
%     100 100 100 100 100 100];
%     
% 
% x1 = [0 1 2 3 4 5];
% x2 = [6 7 8 9 10 11];
% x3 = [12 13 14 15 16 17];
% 
% y1 = [100 75 75 50 10 10];
% y2 = [125 125 125 125 125 125];
% y3 = [100 100 100 100 100 100];
% 
% blue = [20,20,204];
% green = [0,128,0];
% red = [238,128,19];
% 
% bar(y);
%  
% hold off