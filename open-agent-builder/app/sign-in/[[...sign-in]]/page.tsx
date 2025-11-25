import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background-base">
      <SignIn
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "shadow-lg",
          }
        }}
        routing="path"
        path="/sign-in"
        redirectUrl="/workflows"
        signUpUrl="/sign-up"
      />
    </div>
  )
}
