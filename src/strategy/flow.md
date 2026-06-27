
<!-- # The main plan is that we will create 2 strategies.
# Strategy A : Regime based allocation using the probabities
# Strategy B : Regime based strategies. (after classifying into regimes we will apply regime specific strategy.) -->


# Trading strategy implementation.

## first step that i will be doing is making transitional_forecast.py 

so what it does is simple it will take the vector of today let it be v(t) = [bull_prob, bear_prob, side_prob].
and it returns v(t+1) = T*v(t) where T is the transitional matrix.

## next step that i will be doing is make a strategy_engine.py 

so what it will do is that it will take current regime classification and forecast regime classification and market features as input and then it will generate the signals appropriately.

## Strategy A

we use state probabilities but first we define something knowna as state weights thay are just simply mean that if we are 100 percent certain that this is the regime then what percentage of capital will we allocate

The final allocation will be simply the dot product of state probabilites and thier respective weights.


## Strategy B

Here we are going to apply the regime specific strategy logic. I have thought of using both the predicted state of the HMM model and the probabilites of regime to be in all the states. So we are going to use the predicted state to activate which strategy to use like mean reversion or momentum and then using the probabilites we are going to decide how intensively we are going to allocate.