import React from 'react';
import { Box, Button, Container, Typography, Grid, Paper } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// Animations
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const float = keyframes`
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
`;

// Custom styled components
const HeroSection = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #002868 0%, #0046ad 100%)', // Dark blue gradient
  color: '#ffffff',
  padding: theme.spacing(12, 2),
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
  minHeight: '80vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const RedAccent = styled(Box)(({ theme }) => ({
  background: '#bf0a30', // Red
  height: '8px',
  width: '100%',
}));

const WhiteSection = styled(Box)(({ theme }) => ({
  background: '#ffffff',
  padding: theme.spacing(8, 0),
}));

const FeatureCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  textAlign: 'center',
  height: '100%',
  transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.shadows[8],
    border: '2px solid #bf0a30',
  },
  animation: `${fadeIn} 0.6s ease-out forwards`,
  animationDelay: props => props.delay || '0s',
  opacity: 0,
}));

const BlueButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#002868',
  color: '#ffffff',
  padding: theme.spacing(1.5, 5),
  fontSize: '1.1rem',
  '&:hover': {
    backgroundColor: '#0046ad',
  },
  borderRadius: '50px',
}));

const RedButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#bf0a30',
  color: '#ffffff',
  padding: theme.spacing(1.5, 5),
  fontSize: '1.1rem',
  '&:hover': {
    backgroundColor: '#d41443',
  },
  borderRadius: '50px',
}));

const Footer = styled(Box)(({ theme }) => ({
  background: '#002868',
  color: '#ffffff',
  padding: theme.spacing(4, 0),
  textAlign: 'center',
}));

const LogoContainer = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(4),
  animation: `${float} 6s ease-in-out infinite`,
}));

const StyledMotionDiv = styled(motion.div)({
  display: 'inline-block',
});

const Landing = () => {
  const navigate = useNavigate();

  // Animation variants for framer-motion
  const featureVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: i => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.2,
        duration: 0.5,
        ease: "easeOut"
      }
    })
  };

  return (
    <Box>
      <RedAccent />
      
      {/* Hero Section */}
      <HeroSection>
        <Container maxWidth="md">
          <LogoContainer>
            <Typography 
              variant="h1" 
              component="h1" 
              fontWeight="bold"
              sx={{ 
                mb: 2,
                fontSize: { xs: '3rem', sm: '5rem', md: '6rem' },
                letterSpacing: '-0.02em',
              }}
            >
              <span style={{ color: '#bf0a30' }}>Cougar</span>
              <span style={{ color: '#ffffff' }}>Wise</span>
            </Typography>
          </LogoContainer>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <Typography 
              variant="h5" 
              component="h2"
              sx={{ 
                mb: 4,
                fontSize: { xs: '1.2rem', sm: '1.5rem' },
                maxWidth: '800px',
                margin: '0 auto',
                lineHeight: 1.6
              }}
            >
              Your intelligent financial companion built for college students. Track expenses, create budgets, set goals, and get personalized financial advice all in one place.
            </Typography>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
              <RedButton 
                variant="contained" 
                size="large"
                onClick={() => navigate('/register')}
              >
                Get Started
              </RedButton>
              <BlueButton 
                variant="contained" 
                size="large"
                onClick={() => navigate('/login')}
              >
                Log In
              </BlueButton>
            </Box>
          </motion.div>
        </Container>
      </HeroSection>

      {/* Features Section */}
      <WhiteSection>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Typography 
              variant="h3" 
              component="h2" 
              textAlign="center"
              color="#002868"
              fontWeight="bold"
              sx={{ mb: 6 }}
            >
              Manage Your Finances Wisely
            </Typography>
          </motion.div>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <StyledMotionDiv
                custom={0}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={featureVariants}
              >
                <FeatureCard elevation={3} delay="0.2s">
                  <Typography variant="h5" fontWeight="bold" color="#002868" gutterBottom>
                    Budget Planning
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Create customized budgets that fit your college lifestyle and track your spending habits.
                  </Typography>
                  <RedButton onClick={() => navigate('/budget')}>Learn More</RedButton>
                </FeatureCard>
              </StyledMotionDiv>
            </Grid>
            <Grid item xs={12} md={4}>
              <StyledMotionDiv
                custom={1}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={featureVariants}
              >
                <FeatureCard elevation={3} delay="0.4s">
                  <Typography variant="h5" fontWeight="bold" color="#002868" gutterBottom>
                    Financial Analysis
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Get insights into your spending patterns with visual graphs and detailed reports.
                  </Typography>
                  <RedButton onClick={() => navigate('/analysis')}>Learn More</RedButton>
                </FeatureCard>
              </StyledMotionDiv>
            </Grid>
            <Grid item xs={12} md={4}>
              <StyledMotionDiv
                custom={2}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={featureVariants}
              >
                <FeatureCard elevation={3} delay="0.6s">
                  <Typography variant="h5" fontWeight="bold" color="#002868" gutterBottom>
                    AI Assistant
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Receive personalized financial advice and answers to your money management questions.
                  </Typography>
                  <RedButton onClick={() => navigate('/aiassistant')}>Learn More</RedButton>
                </FeatureCard>
              </StyledMotionDiv>
            </Grid>
          </Grid>
        </Container>
      </WhiteSection>

      {/* CTA Section */}
      <Box sx={{ background: '#bf0a30', color: '#ffffff', py: 8, textAlign: 'center' }}>
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Ready to Take Control of Your Finances?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4 }}>
              Join CougarWise today and start building a solid financial foundation.
            </Typography>
            <BlueButton 
              variant="contained" 
              size="large"
              onClick={() => navigate('/register')}
              sx={{ px: 6, py: 1.5 }}
            >
              Sign Up Now
            </BlueButton>
          </motion.div>
        </Container>
      </Box>

      {/* Footer */}
      <Footer>
        <Container>
          <Typography variant="body1">
            © {new Date().getFullYear()} CougarWise - Financial Management for College Students
          </Typography>
        </Container>
      </Footer>
    </Box>
  );
};

export default Landing; 