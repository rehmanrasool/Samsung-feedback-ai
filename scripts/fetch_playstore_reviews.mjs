// const gplay = require('google-play-scraper');
// const fs = require('fs');

import gplay from "google-play-scraper";
import fs from 'fs';



async function fetchReviews(){

//     gplay.app({appId: 'com.samsung.ecomm.global.in'})
//   .then(console.log, console.log);

  

const results =await gplay.reviews({
  appId: 'com.samsung.ecomm.global.in',
  sort: gplay.sort.NEWEST,
  num:1000,
  throttle:10
});
fs.writeFileSync('bad_reviews.json',JSON.stringify(results,null,2));
console.log(`Fetched ${results} reviews`);
}

(async ()=>{
    await fetchReviews()
})()


