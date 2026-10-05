{-# OPTIONS_GHC -Wunused-imports #-}

{-# LANGUAGE CPP             #-}
{-# LANGUAGE TemplateHaskell #-}

{-# OPTIONS_GHC -Wno-overlapping-patterns #-}

module Agda.VersionCommit where

#ifdef VERSION_WITH_GIT_HASH
import Development.GitRev
#endif

import Agda.Version

-- | Agda's version, tagged as the local nightly build.
versionWithCommitInfo :: String
versionWithCommitInfo = version ++ "-nightly"

-- | Information about current git commit, generated at compile time.
commitInfo :: Maybe String
#ifdef VERSION_WITH_GIT_HASH
commitInfo
  | hash == "UNKNOWN" = Nothing
  | otherwise         = Just $ abbrev hash ++ dirty
  where
    hash = $(gitHash)

    -- Check if any tracked files have uncommitted changes
    dirty | $(gitDirtyTracked) = "-dirty"
          | otherwise          = ""

    -- Abbreviate a commit hash while keeping it unambiguous
    abbrev = take 7
#else
commitInfo = Nothing
#endif
