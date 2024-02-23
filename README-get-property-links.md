# 😱 First time coding in a team

## get-property-links()

I wrote the get-property-links() function.
It takes the base Immoweb URL for Belgian properties for sale and the number of search pages you want it to look at as input, and returns a list of individual property URLS as output.

- visits any number of search pages 
- scrapes their html content 
- retrieves the unique page URL of each property listed on the search page
- saves that URL to a list variable
- saves the list as a CSV file
- returns the list to be used in the rest of the project code

## Where it fits in the overall project

The code I wrote is the ground level of our team's data collection project. The function's output constitutes the input for the higher level scraping code. It also ensures that our team solution is dynamic and that it can collects data on fresh properties, instead of using an outdated list of properties that may have been sold or are no longer listed.

## Runtime
Right now, the code executes for 200 pages (12,000 unique URLs) in ~200 seconds.

Update - after editing the code to use ConcurrentFutures and ThreadPoolExecutor, it now executes for 200 search pages (12,000 unique URLs) in ~56 seconds.

![runtime](time-12k-urls-conc.jpg)


## Special thanks!

To my team mates Karel, Alice and Gerrit! 🦀 🦀 🦀  

