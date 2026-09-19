import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import { useAuth } from '../auth/AuthContext';
import { AiWorkoutScreen } from '../screens/AiWorkoutScreen';
import { DrawCardScreen } from '../screens/DrawCardScreen';
import { WorkoutPlayerScreen } from '../screens/WorkoutPlayerScreen';
import { colors } from '../theme';
import { AuthStack } from './AuthStack';
import { MainTabs } from './MainTabs';
import type { RootStackParamList } from './types';

const Stack = createNativeStackNavigator<RootStackParamList>();

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.bg,
    card: colors.bg,
    text: colors.ink,
    border: colors.line,
    primary: colors.accent,
  },
};

export function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.bg }}>
        <ActivityIndicator color={colors.accent} />
      </View>
    );
  }

  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerShadowVisible: false,
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.ink,
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        {user ? (
          <>
            <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
            <Stack.Screen
              name="DrawCard"
              component={DrawCardScreen}
              options={{ title: 'Draw a card' }}
            />
            <Stack.Screen
              name="AiWorkout"
              component={AiWorkoutScreen}
              options={{ title: 'AI workout' }}
            />
            <Stack.Screen
              name="WorkoutPlayer"
              component={WorkoutPlayerScreen}
              options={{ title: 'Workout' }}
            />
          </>
        ) : (
          <Stack.Screen name="Auth" component={AuthStack} options={{ headerShown: false }} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
