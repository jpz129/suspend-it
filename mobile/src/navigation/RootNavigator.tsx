import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { ActivityIndicator, View } from "react-native";

import { useAuth } from "../auth/AuthContext";
import { AiWorkoutScreen } from "../screens/AiWorkoutScreen";
import { DrawCardScreen, PlanScreen } from "../screens/DrawCardScreen";
import { HistoryScreen } from "../screens/HistoryScreen";
import { HomeScreen } from "../screens/HomeScreen";
import { LoginScreen } from "../screens/LoginScreen";
import { RegisterScreen } from "../screens/RegisterScreen";
import { SettingsScreen } from "../screens/SettingsScreen";
import { WorkoutPlayerScreen } from "../screens/WorkoutPlayerScreen";

const AuthStack = createNativeStackNavigator();
const HomeStack = createNativeStackNavigator();
const Tabs = createBottomTabNavigator();

function HomeStackNav() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="Home" component={HomeScreen} />
      <HomeStack.Screen name="DrawCard" component={DrawCardScreen} options={{ title: "Draw a card" }} />
      <HomeStack.Screen name="AiWorkout" component={AiWorkoutScreen} options={{ title: "AI workout" }} />
      <HomeStack.Screen name="Plan" component={PlanScreen} options={{ title: "Your cards" }} />
      <HomeStack.Screen name="Player" component={WorkoutPlayerScreen} options={{ title: "Workout" }} />
    </HomeStack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tabs.Navigator>
      <Tabs.Screen name="Train" component={HomeStackNav} options={{ headerShown: false }} />
      <Tabs.Screen name="HistoryTab" component={HistoryScreen} options={{ title: "History" }} />
      <Tabs.Screen name="Settings" component={SettingsScreen} />
    </Tabs.Navigator>
  );
}

export function RootNavigator() {
  const { token, ready } = useAuth();
  if (!ready) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }
  return (
    <NavigationContainer>
      {token ? (
        <MainTabs />
      ) : (
        <AuthStack.Navigator>
          <AuthStack.Screen name="Login" component={LoginScreen} />
          <AuthStack.Screen name="Register" component={RegisterScreen} />
        </AuthStack.Navigator>
      )}
    </NavigationContainer>
  );
}
