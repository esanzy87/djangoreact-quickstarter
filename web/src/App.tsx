import React, { Suspense } from 'react';
import { BrowserRouter, Route } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Provider } from 'react-redux';
import { createStore, compose, applyMiddleware, combineReducers } from 'redux';
import ReduxPromise from 'redux-promise';
import ReduxThunk from 'redux-thunk';
import { composeWithDevTools } from 'redux-devtools-extension';
import routes from 'src/routes';

const rootReducer = combineReducers({});

const middlewares = [ReduxPromise, ReduxThunk];
const enhancer = 
  process.env.NODE_ENV === 'production'
    ? compose(applyMiddleware(...middlewares))
    : composeWithDevTools(applyMiddleware(...middlewares))
const store = createStore(rootReducer, enhancer);

function App() {
  return (
    <>
      <Helmet>
        <meta charSet='utf=8' />
        <title>흐름가계부</title>
      </Helmet>
      <div className="App">
        <Provider store={store}>
          <BrowserRouter>
            <Suspense fallback={() => <>loading...</>}>
              {routes.map((route) => (
                <Route
                  key={route.name}
                  path={route.path}
                  exact={route.exact}
                  component={route.component}
                />
              ))}
            </Suspense>
          </BrowserRouter>
        </Provider>
      </div>
    </>
  );
}

export default App;
