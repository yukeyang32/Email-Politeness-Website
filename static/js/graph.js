// var average_politeness, average_sentiment, user_politeness, user_sentiment;
// var politeBar, politeTrace, sentiBar, sentiTrace, pieChart;
// var politeBarOptions, politeLineOptions, sentiBarOptions, sentiLineOptions, pieOptions;
// var tempData;

// var color1 = '#E2711D', color2 = '#FF9505', color3 = '#FFB627', color4 = '#FFC971';
// var colors = [color1, color2, color3, color4];
// var currentColor = [];
// var colorMap = new Map();
// // Library Loader
// google.charts.load('current', {'packages':['corechart']});

// socket.on('graph initiation', function(data){

//   console.log(data);
//   tempData = data;

//   google.charts.setOnLoadCallback(function(){
//     draw(tempData);
//     $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
//       draw(tempData);
//     });
//   });
// });

// socket.on('redraw graph', function(data){
//   tempData = data;
//   draw(data);
// });

// $(window).on('resize', function(){
//   draw(tempData);
// });

// function draw(data){
//   colorMap = new Map();
//   currentColor = [];
//   // politeness bar, sentiment bar, talktiveness pie
//   average_politeness = new google.visualization.DataTable();
//   average_politeness.addColumn('string', 'User');
//   average_politeness.addColumn('number', 'Average Politeness Score');
//   average_politeness.addColumn({type: 'string', role: 'style'});

//   talktiveness = new google.visualization.DataTable();
//   talktiveness.addColumn('string', 'User');
//   talktiveness.addColumn('number', 'Contribution to the Conversation');

//   for (var i = 0; i<data[0].length; i++){

//     record = data[0][i];
//     average_politeness.addRows([[record[0], record[1], colors[i]]]);
//     colorMap.set(record[0], colors[i]);
//     talktiveness.addRows([[record[0], record[3]]]);
//     currentUser = record[0];

//     average_sentiment = new google.visualization.DataTable();
//     average_sentiment.addColumn('string', 'Sentiment Type');
//     average_sentiment.addColumn('number', 'Number of Messages');
//     average_sentiment.addRows([['positive', record[2][0]]]);
//     average_sentiment.addRows([['neutral', record[2][1]]]);
//     average_sentiment.addRows([['negative', record[2][2]]]);

//     sentiPieOptions = {
//       title: currentUser,
//       titleTextStyle: {fontSize: 14, bold:false},
//       legend: {position: "none"},
//       tooltip: {trigger: "focus"},
//       pieSliceText: 'label',
//       pieSliceTextStyle: {color: 'black'},
//       slices: {
//         0: { color: posColor },
//         1: { color: neuColor },
//         2: { color: negColor }
//       }
//     };

//     sentiBar = new google.visualization.PieChart(document.getElementById('sentiment_pie_user' + i));
//     sentiBar.draw(average_sentiment, sentiPieOptions);
//   }

//   // politeness trace, sentiment trace
//   user_politeness = new google.visualization.DataTable();
//   user_politeness.addColumn('string', 'Time');
//   user_sentiment = new google.visualization.DataTable();
//   user_sentiment.addColumn('string', 'User');
//   user_sentiment.addColumn('number', 'Positive');
//   user_sentiment.addColumn('number', 'Neutral');
//   user_sentiment.addColumn('number', 'Negative');

//   politeness = data[1]['politeness'];
//   sentiment = data[1]['sentiment'];


//   var users = [];

//   for (record in politeness){
//     for (user in politeness[record]){
//       if (!users.includes(politeness[record][user][0])){
//         users.push(politeness[record][user][0]);
//         user_politeness.addColumn('number', politeness[record][user][0]);
//       }
//     }
//   }

//   var numCol = user_politeness.getNumberOfColumns();

//   for (record in politeness){
//     var row1 = [];
//     row1.push(record);
//     while (row1.length < numCol){
//       row1.push(0);
//     }
//     for (user in politeness[record]){
//       if (!currentColor.includes(colorMap.get(politeness[record][user][0]))){
//         currentColor.push(colorMap.get(politeness[record][user][0]));
//       }
//       row1[users.indexOf(politeness[record][user][0]) + 1] = politeness[record][user][1];
//     }
//     user_politeness.addRow(row1);
//   }

//   // 'sentiment': {'5:43 PM': [('ss', 0, 1, 0)], '5:44 PM': [('ss', 0, 1, 0)]}}

//   console.log(sentiment);
//   for (record in sentiment){ // time
//     for (sub in sentiment[record]){ // user info in that minute
//       user_sentiment.addRows([sentiment[record][sub]]);
//     }
//     user_sentiment.addRows([['', null, null, null]]);
//   }

//   politeBarOptions = {
//     title: 'Average Politeness Score',
//     tooltip:{ignoreBounds:false},
//     chartArea: {width:'85%'},
//     vAxis: { ticks: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] },
//     hAxis: {maxAlternation: 1},
//     legend: { position: "none" }
//   };

//   pieOptions = {
//     title: 'Talktiveness Pie',
//     tooltip: {ignoreBounds: false},
//     pieHole: 0.3,
//     chartArea: {width:'85%'},
//     slices: {
//       0: { color: color1 },
//       1: { color: color2 },
//       2: { color: color3 },
//       3: { color: color4 }
//     }
//   };

//   politeLineOptions = {
//     title: 'Politeness Scores in the Past 5 Minutes',
//     vAxis: { ticks: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]},
//     hAxis: {maxAlternation: 1},
//     legend: { position: "bottom" },
//     chartArea: {width:'85%'},
//     series: {
//       0: { color: currentColor[0] },
//       1: { color: currentColor[1] },
//       2: { color: currentColor[2] },
//       3: { color: currentColor[3] }
//     }
//   };

//   sentiLineOptions = {
//     title: 'Sentiment Composition in the Past 5 Minutes',
//     vAxis: { format: 0 },
//     hAxis: {maxAlternation: 1},
//     isStacked: true,
//     legend: { position: "bottom" },
//     chartArea: {width:'85%'},
//     series: {
//       0: { color: posColor },
//       1: { color: neuColor },
//       2: { color: negColor },
//     }
//   };

//   politeBar = new google.visualization.ColumnChart(document.getElementById('politeness_bar'));
//   pieChart = new google.visualization.PieChart(document.getElementById('talktiveness_pie'));
//   politeTrace = new google.visualization.ColumnChart(document.getElementById('politeness_trace'));
//   sentiTrace = new google.visualization.ColumnChart(document.getElementById('sentiment_trace'));
//   google.visualization.events.addListener(politeTrace, 'error', errorHandler1);
//   google.visualization.events.addListener(politeBar, 'error', errorHandler2);
//   google.visualization.events.addListener(sentiTrace, 'error', errorHandler3);
//   google.visualization.events.addListener(pieChart, 'error', errorHandler5);

//   politeBar.draw(average_politeness, politeBarOptions);
//   pieChart.draw(talktiveness, pieOptions);
//   politeTrace.draw(user_politeness, politeLineOptions);
//   sentiTrace.draw(user_sentiment, sentiLineOptions);
// }

// function errorHandler1(errorMessage) {
//     google.visualization.errors.removeError(errorMessage.id);
//     google.visualization.errors.addError(document.getElementById('politeness_trace'), 'No stats to display yet!', '', {style: 'background-color: black; font-size: 16px; margin: 10% 20%;'});
// }

// function errorHandler2(errorMessage) {
//     google.visualization.errors.removeError(errorMessage.id);
//     google.visualization.errors.addError(document.getElementById('politeness_bar'), 'No stats to display yet!', '', {style: 'background-color: black; font-size: 16px; margin: 10% 20%;'});
// }

// function errorHandler3(errorMessage) {
//     google.visualization.errors.removeError(errorMessage.id);
//     google.visualization.errors.addError(document.getElementById('sentiment_trace'), 'No stats to display yet!', '', {style: 'background-color: black; font-size: 16px; margin: 10% 20%;'});
// }

// function errorHandler4(errorMessage) {
//     google.visualization.errors.removeError(errorMessage.id);
//     google.visualization.errors.addError(document.getElementById('sentiment_bar'), 'No stats to display yet!', '', {style: 'background-color: black; font-size: 16px; margin: 10% 20%;'});
// }

// function errorHandler5(errorMessage) {
//     google.visualization.errors.removeError(errorMessage.id);
//     google.visualization.errors.addError(document.getElementById('talktiveness_pie'), 'No stats to display yet!', '', {style: 'background-color: black; font-size: 16px; margin: 10% 20%;'});
// }

// // obsolete code:

// // switch(this.innerHTML){
// //   case 'Politeness':
// //     politeTrace.draw(user_politeness, politeLineOptions);
// //     politeBar.draw(average_politeness, politeBarOptions);
// //     break;
// //   case 'Sentiment':
// //     sentiTrace.draw(user_sentiment, sentiLineOptions);
// //     sentiBar.draw(average_sentiment, sentiBarOptions);
// //     break;
// //   case 'Talktiveness':
// //     pieChart.draw(talktiveness, pieOptions);
// //     break;
// // }

// // user_politeness.addColumn('string', 'Message');
// // user_sentiment.addColumn('string', 'Message');
// // create an array full of nulls
// // var maxLen = -1;
// // var count = 0;
// // for (record in politeness){ // same as for record in sentiment
// //   user_politeness.addColumn('number', record);
// //   user_sentiment.addColumn('number', record);
// //   count ++;
// //   if (maxLen==-1 ){
// //     maxLen = politeness[record].length;
// //   }
// //   else if (politeness[record].length > maxLen){
// //     maxLen = politeness[record].length;
// //   }
// // }
// //
// // for (var i=0; i < maxLen; i++){
// //   user_politeness.addRow(new Array(count+1).fill(null));
// //   user_sentiment.addRow(new Array(count+1).fill(null));
// //   user_politeness.setCell(i, 0, (i+1).toString()); // msg indices
// //   user_sentiment.setCell(i, 0, (i+1).toString());
// // }
// //
// // var col = 1;
// // for (record in politeness){
// //   for (var j = 0; j < politeness[record].length; j++){
// //     user_politeness.setCell(j, col, politeness[record][j]);
// //     user_sentiment.setCell(j, col, sentiment[record][j]);
// //   }
// //   col++;
// // }
