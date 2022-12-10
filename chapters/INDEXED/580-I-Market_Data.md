<div style='page-break-after: always; break-after: always;'></div>

# Appendix I: Market Data

Given the arguments made so far, it should not be surprising that certain patterns exist, albeit obscured, within seemingly random data, such as the stock market.

One test that anyone can test for themselves shows such a hidden pattern.  In the example, we are 14 months of data (632,869 values) from the 1-minute chart of Bitcoin/ USD-Tether (BTC/USDT) from the Binance exchange from Jan 1, 2021, to Feb 14, 2022.

Start at the beginning of the data and take a series of values, such as 16, 24, 32, etc., consecutive values.  In this example, we will use 16  consecutive values.  This means we have a 632,853 (or 632,869 - 16) sets of 16 values that looks something like:

*Raw data*

```
     1: [19695.49, 19646.79, 19607.03, ..., 19537.95]
        ...
632853: [42136.31, 42164.06, 42129.1, ..., 42194.44]
```

Then ‘normalize’ the data to reduce each set’s values within the range of -0.5 to +0.5:

*Normalized data*

```
     1: [0.5, 0.20914, -0.02830, .... -0.44087]
        ...
632853: [-0.38965, 0.035047, -0.5, ..., 0.5]
```

Then apply a moving average (of 3) to these normalized values:

*Mean data*

```
     1: [0.5, 0.20914, -0.02830,..., -0.44087]
        ...
632853: [-0.38965, 0.03504, -0.5, ..., 0.5]
```

Finally, round these values to a single digit:

*Rounded data*

```
    1:  [5, 2, 0, ...,-4]
        ...
632853: [-4, 0, -5, ..., 5]
```

The purpose of the above is to create sets of single values that represent the original values and, in the process, remove the ‘noise’ in the data.

We then split each set into two parts, the first 8 values and the last 8 values, sum the values of each part, and subtract the 1<sup>st</sup> part from the 2<sup>nd</sup> part.

For example, if we were using sets of 8 values, we’d have sets that look like this:

```
[-4, 0, -5, -3, -4, 1, -1, 5]
```

Splitting and summing the 1<sup>st</sup> part results in **-12** *(-4 + 0 + -5 + -3)*, and the 2<sup>nd</sup> part results in **1** *(-4 + 1 + -1 + 5)* .  Therefore, subtracting the 1<sup>st</sup> from the 2<sup>nd</sup> part results in **13** *(1 - -12)*.

We now have a single number representing the relationship between the first and last half of every set.  

We'll call these values ***s1*** for the 1<sup>st</sup> part, ***s2*** for the 2<sup>nd</sup> part, and ***sd*** for the difference between ***s2*** and ***s1***.

To equate these values to something meaningful, such as the actual values of the transactions, we apply the same rule and sum all the original values together.  We’ll call that value ***sv***.

There are now 3 values for each set: ***sv***, ***s1***, ***s2***, ***sd***... for example:

```
-5221, -242, 135, -107	 
358483, 69, -20, 49
```

If we plot the actual values (***sv***) against the  difference (***sd***), we see a very familiar form, that of a wave or cycle:

*Note: These plots were made with data sets of 63 values to increase the clarity of the plots*

<center><img src='../Images/sd-plot1a.png' style='width:100%'/></center>

If we plot ***s1*** against ***s2*** we see another familiar form:

<center><img src='../Images/sd-plot2.png' style='width:100%'/></center>

If we look at the plots of ***sv*** against both ***s1*** and ***s2***, we see the following; two opposing ‘waves’, essentially a double helix:

<center><img src='../Images/sd-plot3.png' style='width:100%'/></center>

This tells us that any ***sd*** with a value above 0 will yield profit, and any ***sd*** below 0 will lose money.  The ***sd*** values form a curve, showing that (in this case) an ***s1*** value between 50 and 100 (for 16 values, 100-150 for 63 values) is the most likely to return the most profit in ***s2***.  

In this way, we can predict the future.

This pattern is the same for any size sample, which means it can predict the next 8 minutes or the next 8 hours.

That is the theory, at least.  In actual practice, when applied to trades on the Binance exchange against the 1-minute charts, going long on every transaction that has ***sd*** > 0 (along with some other control parameters) and closing at the first opportunity returns about 50% annually, which seems intuitively correct given we are only looking at 2 “forces”, positive and negative. 

**To further test this…**

Suspecting that my results might be due to something other than what I was testing for, I devised another test that used a different method on different data.  My new algorithm looped through about a million data points of real-time closing prices for BTC/USDT.  At every point, it took the previous 16 values and assigned a 1 to a value greater than the previous value or a 0 if less than the previous value.  I then recorded the original value from positions 0 and 15, the first and last values, of each 16-element array. 

This created 1,000,000 records that looked like:

```
0000000000000000, 20000, 21000
0000000000000000, 21000, 9000
0000000000000001, 32123, 31321
...
1111111111111110, 32101, 34321
1111111111111111, 32101, 34326
```

I wanted only 2<sup>16</sup> (65536) of these records, one for each unique binary value, so I averaged all the amounts that had the same binary pattern (of 16 1s and 0s) to create one record for each of the binary values.  For example, the two entries above of 0000000000000000 now become one entry:

```
0000000000000000, 20500, 15000
```

*(20500 = avg(20000+10000),  15000 = avg(21000+9000)*

Now, there are 65,536 entries, each with the average beginning and ending price of its 16 elements.

I plotted the percentage difference between the beginning price and ending price on the Y-axis and the value of the first 8 bits of each binary value on the X-axis.  My assumption was that the Y-axis values, the % difference, would be generally random, so I was expecting to see something like this:

<center><img src='../Images/perf.png' style='width:100%'/></center>

*The above image is the plot of the average ratio of the number of BULL elements (last price > first price) over BEAR elements (last price < first price) for each binary value that begins with value 0 - 255*

Instead, I got this!

<center><img src='../Images/pffd.png' style='width:100%'/></center>

The above image is just a small set to show the patterns.  Plotting all 64k points looks like this:

<center><img src='../Images/pffd64.png' style='width:100%'/></center>

Sorting the data by % instead of by hex values shows a more linear, less fractal pattern:

<center><img src='../Images/pffd-flipped.png' style='width:50%'/></center>

What is equally surprising (to me, at least) is the stepped aspect of the line.

If the plot is changed to only use the first 8-bit (right) values and not 16-bit (left) values when plotting,  we get the essentially same plot in a series of  ‘octaves’.

<center><img src='../Images/pffd-2.png' style='width:100%'/></center>
This second test suggested that: Any sequential 16 prices (in real time for BTC/USDT at least) will tend to end higher when there are more DOWN than UP values in the first 8 prices and will tend to end lower when there are more UP than DOWN in the last 8, regardless of what the other 8 bits are doing.

This supports the first example that also states that any delta value that is above 0 (meaning the 1<sup>st</sup> part is less than the 2<sup>nd</sup> part,  i.e., there are more DOWN values that UP values in the first part) will yield profit.

The Tholonic idea here is that even within random or unpredictable data, the laws of cause and effect create patterns that create balance.  When there is an imbalance on one side, it is predictable that this will soon be followed by an equal and opposite imbalance.   While it is impossible to predict where the balance point will exist in the future.  Given that there are unpredictable opposing forces constantly exerting pressure, what can be predicted is the potential opposing force to the current dominant force.

**However…**

These patterns are the same for any series of random numbers.  When I ran these same tests using random numbers between 1 and 1,000,000, the result was visually identical.  It works with market data because that, too, is random, for all intents and purposes.  So, while these patterns do not tell us anything new about market data specifically, they do tell us something about the cyclical nature of even the most unpredictable events.

# Applying Newton’s 2<sup>nd</sup> law to the Market

*Note: This is very ‘beta’.*

Here is a more detailed example of the earlier reference to Newton’s law and how it might apply to finance.

Below, in row A, we have the historical price data of the cryptocurrency of Etherium, recorded every 15 minutes from December 12, 7:45, to December 13, 17:25.  The squiggly line is the raw data, and the overlaid smoother line is the moving average of the day’s trades.

<center><img src='../Images/chartcmp.png' style='width:100%'/></center>

We assign the following concepts in the following manner:

**Voltage (V)**, the potential between the highest and lowest points of energy, is assigned to the difference between the *opening* and *closing* price for each 15-minute period, as this represents the price potential for that period.

**Current (I)** is the quantity of energy that is moving, which we assign here to the volume of trades that have taken place in that time period.

With these 2 values, we can calculate the following:

**Resistance (R)** is calculated as R=V&div;I, representing the asset’s theoretically ideal value or price.  We refer to this value as the *Balanced Price*, but in reality, the actual agreed-upon price is rarely this value, as you can see in ***Row G***, which compares the *Balanced Price* (R) with the actual price.  Interestingly, while the *Balanced Price* is calculated, the actual price is the result of the resistance between the seller wanting a higher price and the buyer wanting a lower price.

**Power (P)** is also calculated as R=V&times;I (but it is not clear what P represents yet).

<img src='../Images/ohmslaw-market.png' style='float:right; width:40%'/>In the above image on the right, there is a legend that shows the formulas used to describe these values.  This requires a bit of explanation.  Each value of P, V, I, and R can be calculated using 3 different formulas with the remaining 3 values.  When we do this with electricity or matter, all 3 formulas for each value give the same result, as expected.  Here, however, they give slightly different results.  For example, calculating R<sub>1</sub>=V&div;I, R<sub>2</sub>=V<sup>2</sup>&div;P, and R<sub>3</sub>=P&div;I<sup>2</sup>, we’d expect all three values of R<sub>1</sub>, R<sub>2</sub>, and R<sub>3</sub> to be the same, at least in the case of electricity, but here they are all slightly different.  However, when all 3 band values are added together, they form the exact same pattern as that of R<sub>3</sub>=P&div;I<sup>2</sup>.  This is the same for all 4 formulas, and the above formulas have the same pattern as the totals.  This is why we say the above formulas *describe* rather than *calculate* the values because all 12 formulas can do the *calculations*, but only 4 formulas seem to *describe* them.

The issue here is that even though we should be using the R<sub>3</sub> formula, we can’t because we do not have the values for P, as we only have the values V and I we can only use the R<sub>1</sub> formula.  R<sub>1</sub> and R<sub>3</sub> are not the same, but they are very close (R<sub>1</sub> light, R<sub>2</sub> bold):

<center><img src='../Images/2bands-R1R2.png' style='width:100%'/></center>

If we were to show all 3 R bands, it would look like this:

<center><img src='../Images/3bands-R.png' style='width:100%'/></center>

When these 3 bands are added together to form 1 new band,  we get a single band that, when normalized to the same scale as the single bands, is exactly the same as the single band formed by I<sup>2</sup>/P.

Here are the other bands as well:

<center><img src='../Images/3bands-I.png' style='width:100%'/></center>

<center><img src='../Images/3bands-P.png' style='width:100%'/></center>

<center><img src='../Images/3bands-V.png' style='width:100%'/></center>

This last one is a surprise because we are actually seeing all three bands; they just happen to be exactly the same for all the formulas!

Tholonically, this is very interesting because, if you remember, V is the N-source, and P is the result of the N-child.  If you look at P and V, you will notice how similar they are:

<center><img src='../Images/2bands-PV.png' style='width:100%'/></center>

This would then suggest that I and R should be opposites, which they are:

<center><img src='../Images/2bands-IR.png' style='width:100%'/></center>

We might then expect to see the closing prices fluctuate in-between these two bands, but it seems pretty clear that the closing price follows the R line (below). 

<center><img src='../Images/hist-big-R.png' style='width:100%'/></center>

If we multiply them, we get V, as V=I&times;R, and if we look at the difference between them, we get something very close to R again:

<center><img src='../Images/2bands-IR-R.png' style='width:100%'/></center>

<img src='../Images/bands.png' style='float:right;width:20%'/>In order to make these bands comparable, all the data of all the lines were normalized to the minimum and maximum of the closing prices, but the rise and fall of the values were still too extreme to properly compare.  We took the n<sup>th</sup> root of the number to fix this.  In these examples, n=8 and anything after 8 was pretty similar.  See the charts on the right to understand the ranges for these lines.

The R band appears to be consistently predictive of the closing price, and I suspect that if we understood more about the other lines, we could build a pretty decent market indicator.

This model seems to work better for shorter windows, like 15 minutes, than larger windows, like 24 hours.

As a test, considering we are looking at this tholonically, below is a chart where the black line is the value that is (V&div;R) &times; (V&div;I), which we’re call the *adjusted indicator*.  This curve is similar to the P curve but different enough to make a pattern more obvious.

<center><img src='../Images/adjpricecomp.png' style='width:100%'/></center>

For those who analyze the market, here is this model (applied to the Tradingview platform) applied to stocks, commodities, foreign exchange, and crypto:

<center><img src='../Images/th-stocks.png' style='width:100%'/></center>
